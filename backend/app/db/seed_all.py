"""Comprehensive seed script for Transpop demo data.
Creates realistic Casablanca-based data across all tables.
"""
from __future__ import annotations

import asyncio
import random
import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:password@helium:5432/heliumdb"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
random.seed(42)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
MOROCCAN_FIRST_NAMES_M = ["Mohammed", "Ahmed", "Youssef", "Omar", "Karim",
                           "Hassan", "Rachid", "Khalid", "Hamid", "Aziz",
                           "Mehdi", "Samir", "Nabil", "Tariq", "Hicham"]
MOROCCAN_FIRST_NAMES_F = ["Fatima", "Khadija", "Zineb", "Nadia", "Sara",
                           "Meryem", "Houda", "Layla", "Samira", "Amina",
                           "Soukaina", "Hasnae", "Malak", "Rim", "Ilham"]
MOROCCAN_LAST_NAMES = ["El Mansouri", "Benali", "Alaoui", "El Idrissi",
                        "Hajji", "Chraibi", "Tazi", "Bennani", "Filali",
                        "Berrada", "El Amrani", "Tahiri", "Zerrouki",
                        "Bouhali", "Cherkaoui", "El Fassi", "Benbrahim",
                        "Ouazzani", "El Khatib", "Sabri"]
DEPARTMENTS = ["Production", "Logistique", "Maintenance", "Qualité",
               "Administration", "RH", "Finance", "IT", "Commercial", "Sécurité"]
FUNCTIONS = ["Opérateur", "Technicien", "Ingénieur", "Manager", "Agent",
             "Superviseur", "Coordinateur", "Analyste", "Responsable", "Directeur"]
TRANSPORT_MODES = ["Voiture personnelle", "Taxi", "Bus public",
                   "Covoiturage", "Moto", "À pied"]
SHIFT_TIMES = ["06:00", "07:00", "08:00", "14:00", "22:00"]

NEIGHBORHOODS = [
    ("Ain Chock",       33.5505, -7.5752),
    ("Ain Sebaa",       33.6203, -7.5318),
    ("Anfa",            33.5977, -7.6443),
    ("Belvedere",       33.5975, -7.5750),
    ("Bernoussi",       33.6289, -7.5237),
    ("Bourgogne",       33.5836, -7.6183),
    ("California",      33.5782, -7.6413),
    ("El Fida",         33.5826, -7.5876),
    ("Habous",          33.5718, -7.6099),
    ("Hay Hassani",     33.5575, -7.6535),
    ("Hay Mohammadi",   33.5857, -7.5551),
    ("Maarif",          33.5792, -7.6313),
    ("Sidi Belyout",    33.5917, -7.6059),
    ("Sidi Bernoussi",  33.6265, -7.5211),
    ("CIL",             33.5688, -7.6257),
    ("Oasis",           33.5598, -7.6385),
    ("Racine",          33.5833, -7.6438),
    ("Val Fleuri",      33.5850, -7.5625),
    ("Ben M'Sick",      33.5614, -7.5658),
    ("Sidi Othmane",    33.5552, -7.5605),
]

SITES_DATA = [
    {
        "code": "CAS-AIN",
        "name": "Usine Ain Sebaa",
        "address": "Zone Industrielle d'Ain Sebaa, Route de Moulay Abdallah",
        "city": "Casablanca",
        "lat": 33.6121, "lng": -7.5310,
        "num_shifts": 3,
        "shift_1_entry": time(6, 0),  "shift_1_exit": time(14, 0),
        "shift_2_entry": time(14, 0), "shift_2_exit": time(22, 0),
        "shift_3_entry": time(22, 0), "shift_3_exit": time(6, 0),
        "working_days": "Lundi-Samedi", "days_per_week": 6,
        "contact_name": "Mohammed Benali", "contact_phone": "+212 5 22 60 11 00",
        "zfe_zone": False, "security_profile": "high",
        "access_notes": "Entrée principale Gate A, badge requis",
        "parking_notes": "Parking P1 réservé aux navettes",
    },
    {
        "code": "CAS-BCK",
        "name": "Centre de Distribution Bouskoura",
        "address": "Zone Industrielle Bouskoura, Route de l'Aéroport",
        "city": "Casablanca",
        "lat": 33.4842, "lng": -7.6466,
        "num_shifts": 2,
        "shift_1_entry": time(7, 0),  "shift_1_exit": time(15, 0),
        "shift_2_entry": time(15, 0), "shift_2_exit": time(23, 0),
        "shift_3_entry": None, "shift_3_exit": None,
        "working_days": "Lundi-Vendredi", "days_per_week": 5,
        "contact_name": "Zineb El Idrissi", "contact_phone": "+212 5 22 53 44 00",
        "zfe_zone": False, "security_profile": "normal",
        "access_notes": "Accès via Route de l'Aéroport, signalisation bleue",
        "parking_notes": "Parking navettes côté Est",
    },
    {
        "code": "CAS-MLR",
        "name": "Site Moulay Rachid",
        "address": "Zone Industrielle Moulay Rachid, Rue des Acacias",
        "city": "Casablanca",
        "lat": 33.5472, "lng": -7.5844,
        "num_shifts": 2,
        "shift_1_entry": time(8, 0),  "shift_1_exit": time(17, 0),
        "shift_2_entry": time(17, 0), "shift_2_exit": time(1, 0),
        "shift_3_entry": None, "shift_3_exit": None,
        "working_days": "Lundi-Samedi", "days_per_week": 6,
        "contact_name": "Khalid Chraibi", "contact_phone": "+212 5 22 70 22 00",
        "zfe_zone": True, "security_profile": "normal",
        "access_notes": "Zone ZFE - vignettes obligatoires",
        "parking_notes": "Parking central P0, 40 places navettes",
    },
    {
        "code": "CAS-ACK",
        "name": "Atelier Ain Chock",
        "address": "Quartier Industriel Ain Chock, Boulevard Hassan II",
        "city": "Casablanca",
        "lat": 33.5356, "lng": -7.5753,
        "num_shifts": 1,
        "shift_1_entry": time(8, 0),  "shift_1_exit": time(17, 0),
        "shift_2_entry": None, "shift_2_exit": None,
        "shift_3_entry": None, "shift_3_exit": None,
        "working_days": "Lundi-Vendredi", "days_per_week": 5,
        "contact_name": "Fatima Tazi", "contact_phone": "+212 5 22 82 33 00",
        "zfe_zone": False, "security_profile": "low",
        "access_notes": "Entrée unique Boulevard Hassan II",
        "parking_notes": "Parking visiteurs disponible",
    },
]

VEHICLE_DATA = [
    # (type, brand_model, capacity, owner_type, monthly_cost, monthly_km, motorization, zfe)
    ("minibus",  "Mercedes Sprinter 519",  19, "Propriété", 12500, 4500, "diesel",   False),
    ("minibus",  "Ford Transit 430",       17, "Location",  9800,  3800, "diesel",   False),
    ("midibus",  "Isuzu NQR 70",           30, "Propriété", 18000, 5200, "diesel",   False),
    ("midibus",  "MAN Lion's City M",      32, "Propriété", 21000, 6000, "diesel",   True),
    ("bus",      "Iveco Crossway 10.8m",   50, "Location",  35000, 8000, "diesel",   False),
    ("bus",      "Higer KLQ6109",          49, "Propriété", 28000, 7500, "diesel",   False),
    ("minibus",  "Renault Master L3H2",    17, "Location",  9500,  3600, "diesel",   True),
    ("voiture",  "Dacia Logan MCV",         7, "Propriété", 4500,  2800, "diesel",   False),
    ("voiture",  "Volkswagen Caddy",        6, "Location",  5200,  3000, "diesel",   True),
    ("minibus",  "Toyota HiAce Super LWB", 14, "Propriété", 11000, 4200, "diesel",   False),
    ("midibus",  "King Long XMQ6859",      28, "Location",  19500, 5800, "gnv",      True),
    ("bus",      "Yutong ZK6938H",         45, "Propriété", 32000, 7200, "diesel",   False),
    ("minibus",  "Peugeot Boxer Combi",    16, "Location",  10500, 4000, "diesel",   False),
    ("voiture",  "Renault Trafic",          8, "Propriété", 5800,  3200, "diesel",   True),
    ("minibus",  "Fiat Ducato 50",         17, "Location",  9200,  3700, "diesel",   False),
]

KPI_TYPES = [
    "absence_rate", "transport_coverage", "avg_occupancy_rate",
    "co2_per_employee", "cost_per_trip", "on_time_pct",
    "volunteer_driver_pct", "pmr_coverage"
]

WEATHER_CONDITIONS = [
    "Ensoleillé", "Nuageux", "Partiellement nuageux",
    "Pluie légère", "Brouillard matinal", "Vent fort"
]

LEAVE_TYPES = [
    "Congé annuel", "Congé maladie", "Congé maternité",
    "Congé sans solde", "Récupération", "Formation"
]


def rand_name():
    if random.random() > 0.5:
        fn = random.choice(MOROCCAN_FIRST_NAMES_M)
    else:
        fn = random.choice(MOROCCAN_FIRST_NAMES_F)
    ln = random.choice(MOROCCAN_LAST_NAMES)
    return fn, ln


def rand_location(base_lat, base_lng, radius_deg=0.03):
    lat = base_lat + random.uniform(-radius_deg, radius_deg)
    lng = base_lng + random.uniform(-radius_deg, radius_deg)
    return round(lat, 6), round(lng, 6)


async def run():
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    from app.models.auth import Role, Tenant, User
    from app.models.employee import Employee
    from app.models.financial import (FinancialScenario, ROICalculation,
                                       TCOEntry)
    from app.models.generated_report import GeneratedReport
    from app.models.kpi_snapshot import KPISnapshot
    from app.models.leave import EmployeeLeave
    from app.models.optimization import Cluster, Optimization, Route
    from app.models.scenario import Scenario
    from app.models.settings import ConstraintParam, OptimizationSettings
    from app.models.site import Site
    from app.models.vehicle import Vehicle
    from app.models.weather import WeatherForecast

    async with Session() as db:
        async with db.begin():
            # ------------------------------------------------------------------
            # 1. Fetch existing tenant
            # ------------------------------------------------------------------
            r = await db.execute(select(Tenant))
            tenant = r.scalars().first()
            if tenant is None:
                raise RuntimeError("Run the admin seed first (seed_admin.py)")
            tid = tenant.id
            print(f"Tenant: {tenant.name} ({tid})")

            # ------------------------------------------------------------------
            # 2. Admin role (already exists) — fetch it
            # ------------------------------------------------------------------
            r = await db.execute(select(Role).where(Role.tenant_id == tid))
            existing_roles = {ro.name: ro for ro in r.scalars().all()}

            def _role(name: str, perms: list[str]) -> Role:
                if name in existing_roles:
                    return existing_roles[name]
                ro = Role(id=uuid.uuid4(), tenant_id=tid, name=name,
                          permissions=perms, is_system_role=True)
                db.add(ro)
                return ro

            role_drh = _role("drh",    ["employees:read", "employees:write", "reports:read", "reports:write"])
            role_daf = _role("daf",    ["financial:read", "financial:write", "reports:read"])
            role_sal = _role("salarie",["profile:read"])
            role_ops = _role("operateur", ["optimization:read", "optimization:write", "sites:read"])
            await db.flush()

            # ------------------------------------------------------------------
            # 3. Extra users
            # ------------------------------------------------------------------
            existing_emails = set()
            r2 = await db.execute(select(User).where(User.tenant_id == tid))
            for u in r2.scalars().all():
                existing_emails.add(u.email)

            extra_users = [
                ("drh@transpop.dev",      "Aicha",    "El Mansouri",   role_drh.id),
                ("daf@transpop.dev",      "Youssef",  "Bennani",       role_daf.id),
                ("operateur@transpop.dev","Rachid",   "Tazi",          role_ops.id),
            ]
            for email, fn, ln, rid in extra_users:
                if email not in existing_emails:
                    db.add(User(id=uuid.uuid4(), tenant_id=tid, email=email,
                                password_hash=pwd_context.hash("transpop2024"),
                                first_name=fn, last_name=ln, role_id=rid, is_active=True))
            await db.flush()

            # ------------------------------------------------------------------
            # 4. Sites
            # ------------------------------------------------------------------
            r3 = await db.execute(select(Site).where(Site.tenant_id == tid))
            existing_codes = {s.code for s in r3.scalars().all()}
            sites: list[Site] = []
            for sd in SITES_DATA:
                if sd["code"] in existing_codes:
                    r4 = await db.execute(select(Site).where(Site.code == sd["code"]))
                    sites.append(r4.scalar_one())
                    continue
                s = Site(id=uuid.uuid4(), tenant_id=tid, **sd)
                db.add(s)
                sites.append(s)
            await db.flush()
            print(f"Sites: {len(sites)}")

            # ------------------------------------------------------------------
            # 5. Employees (25 per site = 100 total)
            # ------------------------------------------------------------------
            r5 = await db.execute(
                select(Employee).where(Employee.tenant_id == tid))
            existing_mats = {e.matricule for e in r5.scalars().all()}
            all_employees: list[Employee] = []
            for si, site in enumerate(sites):
                for i in range(25):
                    mat = f"EMP-{si+1:02d}-{i+1:03d}"
                    if mat in existing_mats:
                        continue
                    fn, ln = rand_name()
                    nbhd = random.choice(NEIGHBORHOODS)
                    home_lat, home_lng = rand_location(nbhd[1], nbhd[2], 0.008)
                    is_pmr = (i % 12 == 0)
                    vol_drv = (not is_pmr and i % 5 == 0)
                    e = Employee(
                        id=uuid.uuid4(),
                        tenant_id=tid,
                        matricule=mat,
                        first_name=fn,
                        last_name=ln,
                        site_id=site.id,
                        shift_time=SHIFT_TIMES[i % len(SHIFT_TIMES)],
                        address=f"{random.randint(1, 200)} Rue {random.choice(['Hassan II','Mohammed V','de la Liberté','des Nations','Al Massira'])}",
                        quartier=nbhd[0],
                        city="Casablanca",
                        lat=home_lat,
                        lng=home_lng,
                        preferred_pickup_lat=round(home_lat + random.uniform(-0.002, 0.002), 6),
                        preferred_pickup_lng=round(home_lng + random.uniform(-0.002, 0.002), 6),
                        is_pmr=is_pmr,
                        function_role=random.choice(FUNCTIONS),
                        phone=f"+212 6 {random.randint(10,99):02d} {random.randint(10,99):02d} {random.randint(10,99):02d} {random.randint(10,99):02d}",
                        department=random.choice(DEPARTMENTS),
                        transport_required=True,
                        current_transport_mode=random.choice(TRANSPORT_MODES),
                        opt_in_company_transport=random.choice(["Oui", "Non", "En attente"]),
                        has_private_car=random.choice([True, False]),
                        volunteer_driver=vol_drv,
                        carpool_seats=random.randint(1, 4) if vol_drv else 0,
                        active=True,
                        hire_date=date(2018 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
                    )
                    db.add(e)
                    all_employees.append(e)
            await db.flush()
            print(f"Employees added: {len(all_employees)}")

            # ------------------------------------------------------------------
            # 6. Vehicles (assign to sites)
            # ------------------------------------------------------------------
            r6 = await db.execute(select(Vehicle).where(Vehicle.tenant_id == tid))
            ex_vehicles = r6.scalars().all()
            all_vehicles: list[Vehicle] = list(ex_vehicles)
            if len(all_vehicles) == 0:
                for vi, vd in enumerate(VEHICLE_DATA):
                    vtype, brand, cap, own, mcost, mkm, motor, zfe = vd
                    site = sites[vi % len(sites)]
                    v = Vehicle(
                        id=uuid.uuid4(),
                        tenant_id=tid,
                        type=vtype,
                        brand_model=brand,
                        capacity=cap,
                        year=random.randint(2018, 2023),
                        owner_type=own,
                        monthly_cost_mad=Decimal(str(mcost)),
                        monthly_km=Decimal(str(mkm)),
                        condition=random.choice(["Excellent", "Bon", "Correct"]),
                        site_id=site.id,
                        is_pmr_accessible=(vi % 4 == 0),
                        fuel_consumption=Decimal(str(round(random.uniform(8, 18), 1))),
                        cost_per_km=Decimal(str(round(random.uniform(1.2, 3.5), 2))),
                        motorization=motor,
                        zfe_compliant=zfe,
                        observations=f"Immatriculation: {random.randint(10000,99999)}-A-{random.randint(10,99)}",
                    )
                    db.add(v)
                    all_vehicles.append(v)
                await db.flush()
                print(f"Vehicles added: {len(all_vehicles)}")

            # ------------------------------------------------------------------
            # 7. Optimization runs (one per site, completed)
            # ------------------------------------------------------------------
            r7 = await db.execute(
                select(Optimization).where(Optimization.tenant_id == tid))
            ex_opts = r7.scalars().all()
            all_opts: list[Optimization] = list(ex_opts)

            today = date.today()
            # Only add if fewer than 3
            for oi, site in enumerate(sites[:3]):
                target_d = today - timedelta(days=7 - oi)
                metrics = {
                    "total_employees": 25,
                    "employees_assigned": 23,
                    "employees_excluded_leave": 2,
                    "total_clusters": 5 + oi,
                    "total_vehicles_used": 3 + oi,
                    "avg_occupancy_rate": round(random.uniform(0.72, 0.91), 2),
                    "total_distance_km": round(random.uniform(120, 280), 1),
                    "total_duration_minutes": round(random.uniform(180, 340), 0),
                    "estimated_fuel_liters": round(random.uniform(18, 45), 1),
                    "estimated_fuel_cost_mad": round(random.uniform(220, 560), 0),
                    "co2_estimate_kg": round(random.uniform(48, 120), 1),
                    "time_saved_vs_individual_hours": round(random.uniform(8, 24), 1),
                    "unassigned_clusters": 0,
                }
                opt = Optimization(
                    id=uuid.uuid4(), tenant_id=tid,
                    site_id=site.id,
                    condition_type=random.choice(["normal", "normal", "intemperies"]),
                    status="completed",
                    params={"algorithm": "dbscan", "eps_meters": 800, "min_samples": 3,
                            "max_route_duration_seconds": 5400},
                    metrics=metrics,
                    target_date=target_d,
                    completed_at=datetime(target_d.year, target_d.month, target_d.day,
                                         10, 30, tzinfo=timezone.utc),
                )
                db.add(opt)
                all_opts.append(opt)

            await db.flush()

            # clusters & routes for each new optimization
            site_employees: dict[uuid.UUID, list[Employee]] = {}
            for e in all_employees:
                site_employees.setdefault(e.site_id, []).append(e)

            for opt in all_opts[-3:]:  # only newly added
                site = next(s for s in sites if s.id == opt.site_id)
                emps = site_employees.get(site.id, [])
                if len(emps) == 0:
                    continue
                n_clusters = int(opt.metrics.get("total_clusters", 5))

                # Create clusters
                clusters_created: list[Cluster] = []
                for ci in range(n_clusters):
                    chunk = emps[ci * (len(emps) // n_clusters):(ci + 1) * (len(emps) // n_clusters)]
                    if not chunk:
                        continue
                    clat = round(sum(e.lat or site.lat for e in chunk) / len(chunk), 6)
                    clng = round(sum(e.lng or site.lng for e in chunk) / len(chunk), 6)
                    pmr_count = sum(1 for e in chunk if e.is_pmr)
                    cl = Cluster(
                        id=uuid.uuid4(), optimization_id=opt.id, site_id=site.id,
                        centroid_lat=clat, centroid_lng=clng,
                        employee_count=len(chunk), pmr_count=pmr_count,
                        security_risk_level=random.choice(["low", "low", "medium"]),
                        employee_ids=[e.id for e in chunk],
                    )
                    db.add(cl)
                    clusters_created.append(cl)

                await db.flush()

                # Create routes (one per cluster, using available vehicles)
                avail_vehicles = [v for v in all_vehicles if v.site_id == site.id]
                for ri, cl in enumerate(clusters_created):
                    veh = avail_vehicles[ri % len(avail_vehicles)] if avail_vehicles else None
                    chunk = emps[ri * (len(emps) // n_clusters):(ri + 1) * (len(emps) // n_clusters)]

                    stops = []
                    cum_dist = 0.0
                    for idx, emp in enumerate(chunk):
                        cum_dist += random.uniform(0.8, 3.5) * 1000
                        stops.append({
                            "employee_id": str(emp.id),
                            "lat": emp.lat or site.lat,
                            "lng": emp.lng or site.lng,
                            "is_pickup": True,
                            "eta_seconds": (idx + 1) * random.randint(180, 420),
                            "cumulative_distance_meters": round(cum_dist, 0),
                        })
                    # Final stop: site
                    stops.append({
                        "employee_id": None,
                        "lat": site.lat, "lng": site.lng,
                        "is_pickup": False,
                        "eta_seconds": (len(chunk) + 1) * 400,
                        "cumulative_distance_meters": round(cum_dist + random.uniform(2000, 8000), 0),
                    })

                    total_dist = round(cum_dist / 1000 + random.uniform(2, 8), 2)
                    route = Route(
                        id=uuid.uuid4(), optimization_id=opt.id,
                        vehicle_id=veh.id if veh else None,
                        site_id=site.id, ordered_stops=stops,
                        total_distance_km=Decimal(str(total_dist)),
                        total_time_minutes=Decimal(str(round(total_dist * 4.5, 1))),
                        rti_compliance_pct=Decimal(str(round(random.uniform(0.82, 0.97), 2))),
                    )
                    db.add(route)

            await db.flush()
            print("Optimization data seeded")

            # ------------------------------------------------------------------
            # 8. Financial Scenarios
            # ------------------------------------------------------------------
            r8 = await db.execute(
                select(FinancialScenario).where(FinancialScenario.tenant_id == tid))
            if r8.scalars().first() is None:
                r_user = await db.execute(select(User).where(User.tenant_id == tid))
                admin_user = r_user.scalars().first()
                uid = admin_user.id if admin_user else None

                for fi in range(2):
                    inv_model = ["own_fleet", "lease_fleet"][fi]
                    fs = FinancialScenario(
                        id=uuid.uuid4(), tenant_id=tid,
                        name=f"Scénario {['Flotte Propre 5 ans', 'Leasing 3 ans'][fi]}",
                        investment_model=inv_model,
                        duration_years=[5, 3][fi],
                        fleet_composition={"minibus": 6, "midibus": 3, "bus": 1},
                        params={"discount_rate": 0.08, "annual_inflation": 0.025},
                        results={
                            "tco_total": [1850000, 1320000][fi],
                            "roi_years": [3.2, 2.1][fi],
                            "npv": [420000, 280000][fi],
                            "irr": [0.18, 0.22][fi],
                        },
                        created_by=uid,
                    )
                    db.add(fs)
                    await db.flush()

                    # TCO entries
                    for vtype, qty, price, maint, ekm, akm, rval in [
                        ("minibus", 6, 350000, 35000, Decimal("1.8"), 50000, 80000),
                        ("midibus", 3, 550000, 55000, Decimal("2.2"), 60000, 120000),
                        ("bus",     1, 900000, 90000, Decimal("2.8"), 70000, 200000),
                    ]:
                        tco = TCOEntry(
                            id=uuid.uuid4(),
                            financial_scenario_id=fs.id,
                            vehicle_type=vtype,
                            motorization="diesel",
                            quantity=qty,
                            purchase_price=Decimal(str(price)),
                            annual_maintenance_cost=Decimal(str(maint)),
                            energy_cost_per_km=ekm,
                            annual_km=Decimal(str(akm)),
                            residual_value=Decimal(str(rval)),
                            infrastructure_cost=Decimal("25000"),
                            tco_per_vehicle=Decimal(str(price * 1.4)),
                            tco_total=Decimal(str(price * qty * 1.4)),
                        )
                        db.add(tco)

                    # ROI calculation
                    roi = ROICalculation(
                        id=uuid.uuid4(),
                        financial_scenario_id=fs.id,
                        baseline_absence_rate=Decimal("0.0820"),
                        target_absence_rate=Decimal("0.0550"),
                        headcount=100,
                        daily_cost=Decimal("380.00"),
                        replacement_cost=Decimal("45000.00"),
                        turnover_rate_before=Decimal("0.1800"),
                        turnover_rate_after=Decimal("0.1100"),
                    )
                    db.add(roi)

                await db.flush()
                print("Financial data seeded")

            # ------------------------------------------------------------------
            # 9. Weather Forecasts (30 days, 4 sites)
            # ------------------------------------------------------------------
            r9 = await db.execute(select(WeatherForecast))
            if r9.scalars().first() is None:
                for site in sites:
                    for d in range(-5, 25):
                        forecast_date = today + timedelta(days=d)
                        precip = Decimal(str(round(random.uniform(0, 8) if random.random() < 0.3 else 0, 1)))
                        wf = WeatherForecast(
                            id=uuid.uuid4(), site_id=site.id,
                            date=forecast_date,
                            condition_summary=random.choice(WEATHER_CONDITIONS),
                            precipitation_mm=precip,
                            temp_min_c=Decimal(str(round(random.uniform(10, 18), 1))),
                            temp_max_c=Decimal(str(round(random.uniform(20, 32), 1))),
                            wind_kph=Decimal(str(round(random.uniform(5, 35), 1))),
                            source="OpenWeatherMap",
                        )
                        db.add(wf)
                await db.flush()
                print("Weather forecasts seeded")

            # ------------------------------------------------------------------
            # 10. KPI Snapshots (90 days)
            # ------------------------------------------------------------------
            r10 = await db.execute(select(KPISnapshot).where(KPISnapshot.tenant_id == tid))
            if r10.scalars().first() is None:
                base_vals = {
                    "absence_rate":        {"value": 0.082, "delta": -0.002},
                    "transport_coverage":  {"value": 0.78,  "delta":  0.003},
                    "avg_occupancy_rate":  {"value": 0.81,  "delta":  0.001},
                    "co2_per_employee":    {"value": 1.42,  "delta": -0.012},
                    "cost_per_trip":       {"value": 22.5,  "delta": -0.15},
                    "on_time_pct":         {"value": 0.92,  "delta":  0.002},
                    "volunteer_driver_pct":{"value": 0.14,  "delta":  0.004},
                    "pmr_coverage":        {"value": 1.0,   "delta":  0.0},
                }
                for day_back in range(90, 0, -1):
                    snap_date = today - timedelta(days=day_back)
                    for kpi_type, cfg in base_vals.items():
                        v = cfg["value"] + cfg["delta"] * (90 - day_back)
                        v += random.uniform(-0.005, 0.005)
                        snap = KPISnapshot(
                            id=uuid.uuid4(), tenant_id=tid,
                            site_id=sites[0].id,
                            snapshot_date=snap_date,
                            kpi_type=kpi_type,
                            value={"value": round(v, 4), "unit": "ratio"},
                        )
                        db.add(snap)
                await db.flush()
                print("KPI snapshots seeded")

            # ------------------------------------------------------------------
            # 11. Transport Scenarios
            # ------------------------------------------------------------------
            r11 = await db.execute(select(Scenario).where(Scenario.tenant_id == tid))
            if r11.scalars().first() is None:
                for sc_name, ctype, mult in [
                    ("Plan Standard",   "normal",      1.0),
                    ("Plan Intempéries","intemperies", 1.3),
                    ("Plan Réduit",     "normal",      0.7),
                ]:
                    sc = Scenario(
                        id=uuid.uuid4(), tenant_id=tid, site_id=sites[0].id,
                        condition_type=ctype,
                        demand_multiplier=mult,
                        name=sc_name,
                        custom_params={"reduce_pmr_radius": ctype == "intemperies"},
                        estimated_metrics={
                            "vehicles_needed": round(8 * mult),
                            "total_distance_km": round(210 * mult, 1),
                            "cost_estimate_mad": round(2800 * mult, 0),
                            "coverage_pct": 0.94,
                        },
                    )
                    db.add(sc)
                await db.flush()
                print("Scenarios seeded")

            # ------------------------------------------------------------------
            # 12. Optimization Settings
            # ------------------------------------------------------------------
            r12 = await db.execute(
                select(OptimizationSettings).where(OptimizationSettings.tenant_id == tid))
            if r12.scalars().first() is None:
                os_ = OptimizationSettings(
                    id=uuid.uuid4(), tenant_id=tid,
                    meeting_radius_meters=600.0,
                    max_walking_distance_meters=800.0,
                    max_route_duration_seconds=5400,
                    fuel_cost_per_liter=13.5,
                    fuel_consumption_l_per_100km=14.0,
                    co2_kg_per_liter=2.68,
                    rti_threshold_minutes=15,
                    night_mode_start="22:00",
                    night_mode_end="06:00",
                    min_night_group_size=3,
                )
                db.add(os_)

                for cname, cval, ctype in [
                    ("max_employees_per_vehicle",  "50",    "integer"),
                    ("min_fill_rate",               "0.65",  "float"),
                    ("osrm_timeout_seconds",        "10",    "integer"),
                    ("enable_weather_override",     "true",  "boolean"),
                    ("cluster_algorithm",           "dbscan","string"),
                ]:
                    db.add(ConstraintParam(
                        id=uuid.uuid4(), tenant_id=tid,
                        name=cname, value=cval,
                        value_type=ctype, is_active=True,
                        description=f"Paramètre: {cname}",
                    ))
                await db.flush()
                print("Settings seeded")

            # ------------------------------------------------------------------
            # 13. Leave records
            # ------------------------------------------------------------------
            r13 = await db.execute(select(EmployeeLeave))
            if r13.scalars().first() is None:
                sample_emps = random.sample(all_employees, min(20, len(all_employees)))
                for emp in sample_emps:
                    start = today - timedelta(days=random.randint(-5, 30))
                    duration = random.randint(1, 5)
                    db.add(EmployeeLeave(
                        id=uuid.uuid4(), employee_id=emp.id,
                        leave_type=random.choice(LEAVE_TYPES),
                        start_date=start,
                        end_date=start + timedelta(days=duration),
                        notes="Déclaré via portail RH",
                    ))
                await db.flush()
                print("Leave records seeded")

            # ------------------------------------------------------------------
            # 14. Generated Reports
            # ------------------------------------------------------------------
            r14 = await db.execute(
                select(GeneratedReport).where(GeneratedReport.tenant_id == tid))
            if r14.scalars().first() is None:
                r_user2 = await db.execute(select(User).where(User.tenant_id == tid))
                admin_user2 = r_user2.scalars().first()
                uid2 = admin_user2.id if admin_user2 else None
                for rtype, fmt in [
                    ("optimization_summary", "pdf"),
                    ("kpi_dashboard",        "pdf"),
                    ("tco_analysis",         "xlsx"),
                    ("employee_transport",   "xlsx"),
                    ("co2_report",           "pdf"),
                ]:
                    db.add(GeneratedReport(
                        id=uuid.uuid4(), tenant_id=tid,
                        report_type=rtype, format=fmt,
                        params={"period": "2025-Q4", "site_id": str(sites[0].id)},
                        generated_by=uid2,
                    ))
                await db.flush()
                print("Reports seeded")

    await engine.dispose()
    print("\nAll seed data inserted successfully!")


if __name__ == "__main__":
    asyncio.run(run())
