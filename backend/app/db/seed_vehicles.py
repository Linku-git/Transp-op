from __future__ import annotations

import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial import VehicleReference

logger = logging.getLogger(__name__)

VEHICLE_REFERENCE_DATA: list[dict] = [
    {
        "type": "minibus",
        "capacity_min": 15,
        "capacity_max": 20,
        "length_meters": Decimal("6.50"),
        "motorizations_available": ["diesel", "hybrid", "electric"],
        "recommended_use": "Small clusters or PMR routes",
        "reference_tco_5y": {
            "diesel": 180000,
            "hybrid": 220000,
            "electric": 280000,
        },
        "zfe_compliant": True,
    },
    {
        "type": "midibus",
        "capacity_min": 25,
        "capacity_max": 35,
        "length_meters": Decimal("8.00"),
        "motorizations_available": ["diesel", "hybrid", "electric", "gnv"],
        "recommended_use": "Medium-density routes",
        "reference_tco_5y": {
            "diesel": 250000,
            "hybrid": 300000,
            "electric": 380000,
            "gnv": 270000,
        },
        "zfe_compliant": True,
    },
    {
        "type": "bus_standard",
        "capacity_min": 40,
        "capacity_max": 55,
        "length_meters": Decimal("12.00"),
        "motorizations_available": ["diesel", "hybrid", "electric", "hydrogen"],
        "recommended_use": "High-density trunk routes",
        "reference_tco_5y": {
            "diesel": 350000,
            "hybrid": 420000,
            "electric": 520000,
            "hydrogen": 600000,
        },
        "zfe_compliant": True,
    },
    {
        "type": "grand_bus",
        "capacity_min": 60,
        "capacity_max": 80,
        "length_meters": Decimal("18.00"),
        "motorizations_available": ["diesel", "hybrid", "electric"],
        "recommended_use": "Very high demand, peak hours",
        "reference_tco_5y": {
            "diesel": 500000,
            "hybrid": 580000,
            "electric": 700000,
        },
        "zfe_compliant": True,
    },
    {
        "type": "vehicule_leger",
        "capacity_min": 5,
        "capacity_max": 9,
        "length_meters": Decimal("5.00"),
        "motorizations_available": ["diesel", "hybrid", "electric"],
        "recommended_use": "Last-mile, PMR, or VIP shuttle",
        "reference_tco_5y": {
            "diesel": 80000,
            "hybrid": 100000,
            "electric": 130000,
        },
        "zfe_compliant": True,
    },
]


async def seed_vehicle_references(db: AsyncSession) -> int:
    """Seed vehicle reference catalog. Returns number of records created."""
    result = await db.execute(
        select(VehicleReference.type)
    )
    existing_types: set[str] = {row[0] for row in result.all()}

    created = 0
    for data in VEHICLE_REFERENCE_DATA:
        if data["type"] in existing_types:
            logger.debug(
                "Vehicle reference '%s' already exists, skipping", data["type"]
            )
            continue

        vehicle_ref = VehicleReference(**data)
        db.add(vehicle_ref)
        created += 1
        logger.info("Created vehicle reference: %s", data["type"])

    if created > 0:
        await db.flush()
        logger.info("Seeded %d vehicle reference(s)", created)
    else:
        logger.info("All vehicle references already exist, nothing to seed")

    return created
