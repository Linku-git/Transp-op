from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.modal import EmployeeModal
from app.models.optimization import Optimization
from app.models.vehicle import Vehicle

logger = logging.getLogger(__name__)

# Constants
CO2_KG_PER_KM_PRIVATE_CAR = 0.12  # Average CO2 emission per km for a private car
WORKING_DAYS_PER_YEAR = 220
TRIPS_PER_DAY = 2  # Round trip


# ---------------------------------------------------------------------------
# CO2 Savings
# ---------------------------------------------------------------------------


async def compute_co2_savings(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    Compute CO2 savings from company transport vs all-private-car baseline.

    Baseline = employee_count x avg_distance_km x 2 trips x working_days x 0.12 kg/km
    Actual = sum of total_co2_kg from completed optimizations.
    """
    base_filter = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]

    # Count active employees
    emp_count_stmt = select(func.count()).select_from(Employee).where(*base_filter)
    employee_count = (await db.execute(emp_count_stmt)).scalar_one()

    # Average commute distance from modal data
    avg_dist_stmt = (
        select(func.coalesce(func.avg(EmployeeModal.distance_km), 0))
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*base_filter)
    )
    avg_distance_km = float((await db.execute(avg_dist_stmt)).scalar_one())

    # Baseline CO2: if everyone drove private cars
    co2_baseline_kg = round(
        employee_count * avg_distance_km * TRIPS_PER_DAY * WORKING_DAYS_PER_YEAR * CO2_KG_PER_KM_PRIVATE_CAR,
        2,
    )

    # Actual CO2 from completed optimizations
    co2_actual_stmt = (
        select(func.coalesce(func.sum(Optimization.metrics["total_co2_kg"].as_float()), 0))
        .where(
            Optimization.tenant_id == tenant_id,
            Optimization.status == "completed",
        )
    )
    co2_actual_kg = round(float((await db.execute(co2_actual_stmt)).scalar_one()), 2)

    co2_saved_kg = round(co2_baseline_kg - co2_actual_kg, 2)
    co2_saved_pct = round(co2_saved_kg / co2_baseline_kg * 100, 1) if co2_baseline_kg > 0 else 0

    # Trend: CO2 saved per optimization run
    trend_stmt = (
        select(
            Optimization.completed_at,
            Optimization.metrics["total_co2_kg"].as_float().label("co2_kg"),
        )
        .where(
            Optimization.tenant_id == tenant_id,
            Optimization.status == "completed",
            Optimization.completed_at.isnot(None),
        )
        .order_by(Optimization.completed_at.asc())
        .limit(50)
    )
    trend_rows = (await db.execute(trend_stmt)).all()

    trend = [
        {
            "date": row.completed_at.isoformat() if row.completed_at else None,
            "co2_saved_kg": round(co2_baseline_kg / max(len(trend_rows), 1) - float(row.co2_kg or 0), 2),
        }
        for row in trend_rows
    ]

    logger.info(
        "CO2 savings computed for tenant %s: baseline=%.1f actual=%.1f saved=%.1f (%.1f%%)",
        tenant_id, co2_baseline_kg, co2_actual_kg, co2_saved_kg, co2_saved_pct,
    )

    return {
        "co2_baseline_kg": co2_baseline_kg,
        "co2_actual_kg": co2_actual_kg,
        "co2_saved_kg": co2_saved_kg,
        "co2_saved_pct": co2_saved_pct,
        "employee_count": employee_count,
        "avg_distance_km": round(avg_distance_km, 2),
        "trend": trend,
    }


# ---------------------------------------------------------------------------
# Private Vehicles Avoided
# ---------------------------------------------------------------------------


async def compute_private_vehicles_avoided(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    Count employees who have a private car but opted for company transport.

    These are vehicles avoided on the road each day.
    """
    base_filter = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]

    # Total employees with a private car
    total_with_car_stmt = (
        select(func.count())
        .select_from(Employee)
        .where(*base_filter, Employee.has_private_car.is_(True))
    )
    total_with_car = (await db.execute(total_with_car_stmt)).scalar_one()

    # Employees with car who opted in to company transport
    avoided_stmt = (
        select(func.count())
        .select_from(Employee)
        .where(
            *base_filter,
            Employee.has_private_car.is_(True),
            Employee.opt_in_company_transport == "Oui",
        )
    )
    vehicles_avoided = (await db.execute(avoided_stmt)).scalar_one()

    adoption_pct = round(vehicles_avoided / total_with_car * 100, 1) if total_with_car > 0 else 0

    return {
        "vehicles_avoided": vehicles_avoided,
        "total_with_car": total_with_car,
        "adoption_pct": adoption_pct,
    }


# ---------------------------------------------------------------------------
# Modal Distribution
# ---------------------------------------------------------------------------

# Mode categories
SOFT_MODES = {"velo", "marche", "trottinette", "a_pied"}
ELECTRIC_MODES = {"electrique", "vehicule_electrique", "vae"}
SHARED_MODES = {"covoiturage", "transport_entreprise", "bus", "tramway", "train", "metro"}
INDIVIDUAL_MODES = {"voiture", "moto", "scooter"}


def _categorize_mode(mode: str | None) -> str:
    """Categorize a transport mode into soft/electric/shared/individual."""
    if not mode:
        return "unknown"
    mode_lower = mode.lower().strip()
    if mode_lower in SOFT_MODES:
        return "soft"
    if mode_lower in ELECTRIC_MODES:
        return "electric"
    if mode_lower in SHARED_MODES:
        return "shared"
    if mode_lower in INDIVIDUAL_MODES:
        return "individual"
    return "other"


async def compute_modal_distribution(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    Compute transport mode distribution from EmployeeModal data.

    Returns breakdown by mode with percentages, plus category totals.
    Also provides a before/after comparison (before = Employee.current_transport_mode,
    after = EmployeeModal.primary_mode for opted-in employees).
    """
    base_filter = [Employee.tenant_id == tenant_id, Employee.active.is_(True)]

    # Current modal distribution (from EmployeeModal)
    modal_stmt = (
        select(
            EmployeeModal.primary_mode,
            func.count().label("count"),
        )
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*base_filter)
        .group_by(EmployeeModal.primary_mode)
        .order_by(func.count().desc())
    )
    modal_rows = (await db.execute(modal_stmt)).all()

    total_modal = sum(r.count for r in modal_rows)
    by_mode = [
        {
            "mode": r.primary_mode,
            "count": r.count,
            "pct": round(r.count / total_modal * 100, 1) if total_modal > 0 else 0,
            "category": _categorize_mode(r.primary_mode),
        }
        for r in modal_rows
    ]

    # Category percentages
    category_counts: dict[str, int] = {"soft": 0, "electric": 0, "shared": 0, "individual": 0, "other": 0, "unknown": 0}
    for item in by_mode:
        cat = item["category"]
        category_counts[cat] = category_counts.get(cat, 0) + item["count"]

    def _cat_pct(cat: str) -> float:
        return round(category_counts[cat] / total_modal * 100, 1) if total_modal > 0 else 0

    # Before distribution (Employee.current_transport_mode)
    before_stmt = (
        select(
            Employee.current_transport_mode,
            func.count().label("count"),
        )
        .where(*base_filter, Employee.current_transport_mode.isnot(None))
        .group_by(Employee.current_transport_mode)
        .order_by(func.count().desc())
    )
    before_rows = (await db.execute(before_stmt)).all()
    total_before = sum(r.count for r in before_rows)

    before = [
        {
            "mode": r.current_transport_mode,
            "count": r.count,
            "pct": round(r.count / total_before * 100, 1) if total_before > 0 else 0,
        }
        for r in before_rows
    ]

    return {
        "by_mode": by_mode,
        "total_employees": total_modal,
        "soft_pct": _cat_pct("soft"),
        "electric_pct": _cat_pct("electric"),
        "shared_pct": _cat_pct("shared"),
        "individual_pct": _cat_pct("individual"),
        "before": before,
        "after": by_mode,
    }


# ---------------------------------------------------------------------------
# ZFE Compliance
# ---------------------------------------------------------------------------


async def compute_zfe_compliance(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    Compute fleet ZFE (Zone a Faibles Emissions) compliance rate.
    """
    base_filter = [Vehicle.tenant_id == tenant_id]

    total_stmt = select(func.count()).select_from(Vehicle).where(*base_filter)
    total_count = (await db.execute(total_stmt)).scalar_one()

    compliant_stmt = (
        select(func.count())
        .select_from(Vehicle)
        .where(*base_filter, Vehicle.zfe_compliant.is_(True))
    )
    compliant_count = (await db.execute(compliant_stmt)).scalar_one()

    compliance_pct = round(compliant_count / total_count * 100, 1) if total_count > 0 else 0

    # Motorization breakdown
    motor_stmt = (
        select(
            func.coalesce(Vehicle.motorization, "Non defini").label("motorization"),
            func.count().label("count"),
            func.count().filter(Vehicle.zfe_compliant.is_(True)).label("compliant"),
        )
        .where(*base_filter)
        .group_by("motorization")
        .order_by(func.count().desc())
    )
    motor_rows = (await db.execute(motor_stmt)).all()

    by_motorization = [
        {
            "motorization": r.motorization,
            "count": r.count,
            "compliant": r.compliant,
            "pct": round(r.compliant / r.count * 100, 1) if r.count > 0 else 0,
        }
        for r in motor_rows
    ]

    return {
        "compliant_count": compliant_count,
        "total_count": total_count,
        "compliance_pct": compliance_pct,
        "by_motorization": by_motorization,
    }


# ---------------------------------------------------------------------------
# Combined RSE KPIs
# ---------------------------------------------------------------------------


async def compute_rse_kpis(
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """Compute all RSE (Corporate Social Responsibility) KPIs."""
    co2_savings = await compute_co2_savings(tenant_id, db)
    private_vehicles = await compute_private_vehicles_avoided(tenant_id, db)
    modal_distribution = await compute_modal_distribution(tenant_id, db)
    zfe_compliance = await compute_zfe_compliance(tenant_id, db)

    return {
        "co2_savings": co2_savings,
        "private_vehicles_avoided": private_vehicles,
        "modal_distribution": modal_distribution,
        "zfe_compliance": zfe_compliance,
    }


# ---------------------------------------------------------------------------
# DPEF Report Generation (PDF)
# ---------------------------------------------------------------------------


def generate_dpef_pdf(rse_data: dict[str, Any]) -> bytes:
    """
    Generate a DPEF (Declaration de Performance Extra-Financiere) PDF report.

    Uses reportlab to build a professional PDF with RSE metrics.
    """
    import io

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DPEFTitle",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=12,
        textColor=colors.HexColor("#0058be"),
    )
    heading_style = ParagraphStyle(
        "DPEFHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=16,
        spaceAfter=8,
        textColor=colors.HexColor("#191c1e"),
    )
    body_style = styles["BodyText"]

    elements: list = []

    # Title
    elements.append(Paragraph("Rapport DPEF", title_style))
    elements.append(Paragraph("Declaration de Performance Extra-Financiere", body_style))
    elements.append(Spacer(1, 12))

    # --- CO2 Savings ---
    co2 = rse_data.get("co2_savings", {})
    elements.append(Paragraph("1. Economies de CO2", heading_style))

    co2_data = [
        ["Indicateur", "Valeur"],
        ["CO2 de reference (baseline)", f"{co2.get('co2_baseline_kg', 0):,.1f} kg"],
        ["CO2 reel (optimise)", f"{co2.get('co2_actual_kg', 0):,.1f} kg"],
        ["CO2 economise", f"{co2.get('co2_saved_kg', 0):,.1f} kg"],
        ["Reduction", f"{co2.get('co2_saved_pct', 0):.1f}%"],
        ["Employes concernes", str(co2.get("employee_count", 0))],
        ["Distance moyenne", f"{co2.get('avg_distance_km', 0):.1f} km"],
    ]
    co2_table = Table(co2_data, colWidths=[10 * cm, 6 * cm])
    co2_table.setStyle(_table_style())
    elements.append(co2_table)
    elements.append(Spacer(1, 10))

    # --- Private Vehicles Avoided ---
    pv = rse_data.get("private_vehicles_avoided", {})
    elements.append(Paragraph("2. Vehicules Prives Evites", heading_style))

    pv_data = [
        ["Indicateur", "Valeur"],
        ["Vehicules evites / jour", str(pv.get("vehicles_avoided", 0))],
        ["Total employes avec vehicule", str(pv.get("total_with_car", 0))],
        ["Taux d'adoption", f"{pv.get('adoption_pct', 0):.1f}%"],
    ]
    pv_table = Table(pv_data, colWidths=[10 * cm, 6 * cm])
    pv_table.setStyle(_table_style())
    elements.append(pv_table)
    elements.append(Spacer(1, 10))

    # --- Modal Distribution ---
    modal = rse_data.get("modal_distribution", {})
    elements.append(Paragraph("3. Distribution Modale", heading_style))

    modal_data = [
        ["Categorie", "Pourcentage"],
        ["Modes doux (velo, marche, etc.)", f"{modal.get('soft_pct', 0):.1f}%"],
        ["Electrique", f"{modal.get('electric_pct', 0):.1f}%"],
        ["Partage (covoiturage, bus, etc.)", f"{modal.get('shared_pct', 0):.1f}%"],
        ["Individuel (voiture, moto)", f"{modal.get('individual_pct', 0):.1f}%"],
    ]
    modal_table = Table(modal_data, colWidths=[10 * cm, 6 * cm])
    modal_table.setStyle(_table_style())
    elements.append(modal_table)
    elements.append(Spacer(1, 10))

    # Per-mode detail
    by_mode = modal.get("by_mode", [])
    if by_mode:
        elements.append(Paragraph("Detail par mode de transport:", body_style))
        mode_data = [["Mode", "Nombre", "Pourcentage"]]
        for m in by_mode:
            mode_data.append([m["mode"], str(m["count"]), f"{m['pct']:.1f}%"])
        mode_table = Table(mode_data, colWidths=[7 * cm, 4.5 * cm, 4.5 * cm])
        mode_table.setStyle(_table_style())
        elements.append(mode_table)
        elements.append(Spacer(1, 10))

    # --- ZFE Compliance ---
    zfe = rse_data.get("zfe_compliance", {})
    elements.append(Paragraph("4. Conformite ZFE (Zone a Faibles Emissions)", heading_style))

    zfe_data = [
        ["Indicateur", "Valeur"],
        ["Vehicules conformes", str(zfe.get("compliant_count", 0))],
        ["Total vehicules", str(zfe.get("total_count", 0))],
        ["Taux de conformite", f"{zfe.get('compliance_pct', 0):.1f}%"],
    ]
    zfe_table = Table(zfe_data, colWidths=[10 * cm, 6 * cm])
    zfe_table.setStyle(_table_style())
    elements.append(zfe_table)

    # Build PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info("DPEF PDF generated: %d bytes", len(pdf_bytes))
    return pdf_bytes


def _table_style() -> TableStyle:
    """Return a consistent table style for DPEF report tables."""
    from reportlab.lib import colors
    from reportlab.platypus import TableStyle

    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0058be")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c2c6d6")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fb")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ])
