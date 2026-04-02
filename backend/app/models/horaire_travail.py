from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class HoraireTravail(BaseModel):
    """Work schedule / shift definition.

    Columns match the Horaire de Travail XLSX schema:
    - type_horaire  : Type Horaire
    - depart_h1     : Horaire départ (Premier Horaire)
    - retour_h1     : Horaire Retour (Premier Horaire)
    - depart_h2     : Horaire départ (Deuxième Horaire)
    - retour_h2     : Horaire Retour (Deuxième Horaire)
    """

    __tablename__ = "horaire_travail"
    __table_args__ = (
        Index("ix_horaire_travail_tenant", "tenant_id"),
        Index("ix_horaire_travail_site", "site_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )

    type_horaire: Mapped[str] = mapped_column(String(100), nullable=False)

    depart_h1: Mapped[str | None] = mapped_column(String(10), nullable=True)
    retour_h1: Mapped[str | None] = mapped_column(String(10), nullable=True)
    depart_h2: Mapped[str | None] = mapped_column(String(10), nullable=True)
    retour_h2: Mapped[str | None] = mapped_column(String(10), nullable=True)

    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    site: Mapped["Site | None"] = relationship("Site", lazy="selectin")
