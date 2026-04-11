from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.ligne import Ligne
from app.models.od_matrix import ODMatrix
from app.schemas.od_matrix import (
    GeocodingEnrichRequest,
    GeocodingEnrichResponse,
    ODMatrixComputeRequest,
    ODMatrixComputeResponse,
    ODMatrixEntry,
    ODMatrixListResponse,
    ZFEComplianceResponse,
    ZFELigneResult,
    ZFEPointCheckRequest,
    ZFEPointCheckResponse,
)
from app.services.geocoding import geocode_address
from app.services.sotreg.gravity_model import compute_od_from_lignes
from app.services.sotreg.zfe_service import (
    check_ligne_zfe_compliance,
    check_zfe_compliance,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sotreg")


# ---------------------------------------------------------------------------
# POST /sotreg/od-matrix/compute — compute OD matrix from active lignes
# ---------------------------------------------------------------------------


@router.post(
    "/od-matrix/compute",
    response_model=ODMatrixComputeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def compute_od_matrix(
    body: ODMatrixComputeRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ODMatrixComputeResponse:
    """Compute OD matrix from active lignes using the Wilson gravity model."""
    tenant_id = current_user.tenant_id

    # Compute OD pairs from lignes
    od_pairs = await compute_od_from_lignes(
        db, tenant_id, beta=body.beta, k=body.k
    )

    if not od_pairs:
        return ODMatrixComputeResponse(
            entries_computed=0,
            beta_used=body.beta,
            k_used=body.k,
            entries=[],
        )

    # Delete previous OD matrix entries for this tenant
    await db.execute(
        delete(ODMatrix).where(ODMatrix.tenant_id == tenant_id)
    )

    # Persist new entries
    created_entries: list[ODMatrix] = []
    for pair in od_pairs:
        entry = ODMatrix(
            tenant_id=tenant_id,
            ligne_id=uuid.UUID(pair["ligne_id"]) if pair.get("ligne_id") else None,
            origin_zone=pair["origin_name"],
            destination_zone=pair["dest_name"],
            flow_estimate=pair["flow_estimate"],
            distance_km=pair["distance_km"],
            gravity_score=pair["gravity_score"],
            beta_used=body.beta,
        )
        db.add(entry)
        created_entries.append(entry)

    await db.flush()
    for entry in created_entries:
        await db.refresh(entry)

    logger.info(
        "OD matrix computed for tenant %s: %d entries (beta=%.4f, k=%.6f)",
        tenant_id,
        len(created_entries),
        body.beta,
        body.k,
    )

    return ODMatrixComputeResponse(
        entries_computed=len(created_entries),
        beta_used=body.beta,
        k_used=body.k,
        entries=[ODMatrixEntry.model_validate(e) for e in created_entries],
    )


# ---------------------------------------------------------------------------
# GET /sotreg/od-matrix/{ligne_id} — get OD matrix entries for a ligne
# ---------------------------------------------------------------------------


@router.get("/od-matrix/{ligne_id}", response_model=ODMatrixListResponse)
async def get_od_matrix_for_ligne(
    ligne_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "responsable_exploitation")),
    db: AsyncSession = Depends(get_db),
) -> ODMatrixListResponse:
    """Get OD matrix entries for a specific ligne."""
    # Verify the ligne exists and belongs to the tenant
    ligne_stmt = select(Ligne).where(
        Ligne.id == ligne_id,
        Ligne.tenant_id == current_user.tenant_id,
    )
    ligne = (await db.execute(ligne_stmt)).scalar_one_or_none()
    if ligne is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligne not found",
        )

    stmt = (
        select(ODMatrix)
        .where(
            ODMatrix.ligne_id == ligne_id,
            ODMatrix.tenant_id == current_user.tenant_id,
        )
        .order_by(ODMatrix.gravity_score.desc())
    )
    result = await db.execute(stmt)
    entries = list(result.scalars().all())

    beta_used = entries[0].beta_used if entries else 0.08

    return ODMatrixListResponse(
        data=[ODMatrixEntry.model_validate(e) for e in entries],
        total=len(entries),
        beta_used=beta_used,
    )


# ---------------------------------------------------------------------------
# GET /sotreg/od-matrix — get all OD matrix entries for the tenant
# ---------------------------------------------------------------------------


@router.get("/od-matrix", response_model=ODMatrixListResponse)
async def list_od_matrix(
    current_user: User = Depends(require_role("admin", "drh", "responsable_exploitation")),
    db: AsyncSession = Depends(get_db),
) -> ODMatrixListResponse:
    """Get all OD matrix entries for the current tenant."""
    stmt = (
        select(ODMatrix)
        .where(ODMatrix.tenant_id == current_user.tenant_id)
        .order_by(ODMatrix.gravity_score.desc())
    )
    result = await db.execute(stmt)
    entries = list(result.scalars().all())

    beta_used = entries[0].beta_used if entries else 0.08

    return ODMatrixListResponse(
        data=[ODMatrixEntry.model_validate(e) for e in entries],
        total=len(entries),
        beta_used=beta_used,
    )


# ---------------------------------------------------------------------------
# GET /sotreg/zfe/lignes — batch ZFE compliance check for all lignes
# ---------------------------------------------------------------------------


@router.get("/zfe/lignes", response_model=ZFEComplianceResponse)
async def get_lignes_zfe_compliance(
    current_user: User = Depends(require_role("admin", "drh", "responsable_exploitation")),
    db: AsyncSession = Depends(get_db),
) -> ZFEComplianceResponse:
    """Check ZFE compliance for all active transport lines."""
    results = await check_ligne_zfe_compliance(db, current_user.tenant_id)

    zfe_results = [ZFELigneResult(**r) for r in results]
    in_zfe = sum(1 for r in zfe_results if r.any_endpoint_in_zfe)

    return ZFEComplianceResponse(
        total_lignes=len(zfe_results),
        lignes_in_zfe=in_zfe,
        results=zfe_results,
    )


# ---------------------------------------------------------------------------
# POST /sotreg/zfe/check — check a single point for ZFE compliance
# ---------------------------------------------------------------------------


@router.post("/zfe/check", response_model=ZFEPointCheckResponse)
async def check_zfe_point(
    body: ZFEPointCheckRequest,
    current_user: User = Depends(require_role("admin", "drh", "responsable_exploitation")),
) -> ZFEPointCheckResponse:
    """Check if a single coordinate is within a ZFE zone."""
    result = await check_zfe_compliance(body.lat, body.lng)

    return ZFEPointCheckResponse(
        is_in_zfe=result.is_in_zfe,
        zone_name=result.zone_name,
        restriction_level=result.restriction_level,
        allowed_crit_air=result.allowed_crit_air,
        checked_at=result.checked_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# POST /sotreg/lignes/{ligne_id}/geocode — geocode enrichment for a ligne
# ---------------------------------------------------------------------------


@router.post(
    "/lignes/{ligne_id}/geocode",
    response_model=GeocodingEnrichResponse,
)
async def geocode_ligne(
    ligne_id: uuid.UUID,
    body: GeocodingEnrichRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> GeocodingEnrichResponse:
    """Geocode and enrich a ligne with updated coordinates from addresses."""
    stmt = select(Ligne).where(
        Ligne.id == ligne_id,
        Ligne.tenant_id == current_user.tenant_id,
    )
    ligne = (await db.execute(stmt)).scalar_one_or_none()
    if ligne is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligne not found",
        )

    origin_geocoded = False
    dest_geocoded = False

    if body.origin_address:
        coords = await geocode_address(body.origin_address)
        if coords:
            ligne.origin_lat = coords[0]
            ligne.origin_lng = coords[1]
            ligne.origin_geom = func.ST_SetSRID(
                func.ST_MakePoint(coords[1], coords[0]), 4326
            )
            origin_geocoded = True
            logger.info(
                "Ligne %s origin geocoded to (%.4f, %.4f) from '%s'",
                ligne_id,
                coords[0],
                coords[1],
                body.origin_address,
            )

    if body.dest_address:
        coords = await geocode_address(body.dest_address)
        if coords:
            ligne.dest_lat = coords[0]
            ligne.dest_lng = coords[1]
            ligne.dest_geom = func.ST_SetSRID(
                func.ST_MakePoint(coords[1], coords[0]), 4326
            )
            dest_geocoded = True
            logger.info(
                "Ligne %s dest geocoded to (%.4f, %.4f) from '%s'",
                ligne_id,
                coords[0],
                coords[1],
                body.dest_address,
            )

    if origin_geocoded or dest_geocoded:
        await db.flush()
        await db.refresh(ligne)

    return GeocodingEnrichResponse(
        ligne_id=str(ligne.id),
        origin_geocoded=origin_geocoded,
        dest_geocoded=dest_geocoded,
        origin_lat=ligne.origin_lat,
        origin_lng=ligne.origin_lng,
        dest_lat=ligne.dest_lat,
        dest_lng=ligne.dest_lng,
    )
