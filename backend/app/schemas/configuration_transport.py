from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConfigurationTransportCreate(BaseModel):
    plan_id: uuid.UUID
    site_id: uuid.UUID | None = None
    conducteur: str | None = Field(default=None, max_length=200)
    poste: str | None = Field(default=None, max_length=20)
    prestataire: str | None = Field(default=None, max_length=100)
    mle_vehicule: str | None = Field(default=None, max_length=50)
    type_vehicule: str | None = Field(default=None, max_length=50)
    type_moteur: str | None = Field(default=None, max_length=50)
    secteur: str | None = Field(default=None, max_length=100)
    entite: str | None = Field(default=None, max_length=200)
    aller_retour: str | None = Field(default=None, max_length=10)
    shift: str | None = Field(default=None, max_length=10)
    heure_depart: str | None = Field(default=None, max_length=10)
    point_depart: str | None = Field(default=None, max_length=200)
    point_arrivee: str | None = Field(default=None, max_length=200)
    heure_arrivee: str | None = Field(default=None, max_length=10)
    arrets_circuit: str | None = Field(default=None, max_length=500)
    duree_trajet_min: int | None = None
    km: float | None = None
    rot: float | None = None
    t_km: float | None = None
    is_active: bool = True


class ConfigurationTransportUpdate(BaseModel):
    conducteur: str | None = Field(default=None, max_length=200)
    poste: str | None = Field(default=None, max_length=20)
    prestataire: str | None = Field(default=None, max_length=100)
    mle_vehicule: str | None = Field(default=None, max_length=50)
    type_vehicule: str | None = Field(default=None, max_length=50)
    type_moteur: str | None = Field(default=None, max_length=50)
    secteur: str | None = Field(default=None, max_length=100)
    entite: str | None = Field(default=None, max_length=200)
    aller_retour: str | None = Field(default=None, max_length=10)
    shift: str | None = Field(default=None, max_length=10)
    heure_depart: str | None = Field(default=None, max_length=10)
    point_depart: str | None = Field(default=None, max_length=200)
    point_arrivee: str | None = Field(default=None, max_length=200)
    heure_arrivee: str | None = Field(default=None, max_length=10)
    arrets_circuit: str | None = Field(default=None, max_length=500)
    duree_trajet_min: int | None = None
    km: float | None = None
    rot: float | None = None
    t_km: float | None = None
    is_active: bool | None = None


class ConfigurationTransportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    plan_id: uuid.UUID
    site_id: uuid.UUID | None
    conducteur: str | None
    poste: str | None
    prestataire: str | None
    mle_vehicule: str | None
    type_vehicule: str | None
    type_moteur: str | None
    secteur: str | None
    entite: str | None
    aller_retour: str | None
    shift: str | None
    heure_depart: str | None
    point_depart: str | None
    point_arrivee: str | None
    heure_arrivee: str | None
    arrets_circuit: str | None
    duree_trajet_min: int | None
    km: float | None
    rot: float | None
    t_km: float | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    site_name: str | None = None
