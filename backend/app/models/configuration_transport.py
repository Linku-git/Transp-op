from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ConfigurationTransport(BaseModel):
    """One trip row inside a configuration plan (mirrors the XLSX structure)."""

    __tablename__ = "configuration_transport"
    __table_args__ = (
        Index("ix_configuration_transport_tenant", "tenant_id"),
        Index("ix_configuration_transport_plan", "plan_id"),
        Index("ix_configuration_transport_poste", "poste"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("configuration_plan.id", ondelete="CASCADE"),
        nullable=False,
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )

    conducteur: Mapped[str | None] = mapped_column(String(200), nullable=True)
    poste: Mapped[str | None] = mapped_column(String(20), nullable=True)
    prestataire: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mle_vehicule: Mapped[str | None] = mapped_column(String(50), nullable=True)
    type_vehicule: Mapped[str | None] = mapped_column(String(50), nullable=True)
    type_moteur: Mapped[str | None] = mapped_column(String(50), nullable=True)
    secteur: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entite: Mapped[str | None] = mapped_column(String(200), nullable=True)
    aller_retour: Mapped[str | None] = mapped_column(String(10), nullable=True)
    shift: Mapped[str | None] = mapped_column(String(10), nullable=True)
    heure_depart: Mapped[str | None] = mapped_column(String(25), nullable=True)
    point_depart: Mapped[str | None] = mapped_column(String(200), nullable=True)
    point_arrivee: Mapped[str | None] = mapped_column(String(200), nullable=True)
    heure_arrivee: Mapped[str | None] = mapped_column(String(25), nullable=True)
    arrets_circuit: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duree_trajet_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    km: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    rot: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    t_km: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    plan: Mapped[ConfigurationPlan] = relationship(
        "ConfigurationPlan", back_populates="rows", lazy="noload"
    )
    site: Mapped[Site | None] = relationship("Site", lazy="selectin")
