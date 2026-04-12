"""Driver Risk Scoring Service — RandomForest-based telematics risk assessment.

Computes driver risk scores using 8 telematics features with a penalty-based
formula, classifies into risk categories, and trains a RandomForest model
for predictive scoring.

Session 120 — CDC SOTREG v5.0 Module M8/ML.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FEATURE_NAMES: list[str] = [
    "nb_alertes_vitesse",        # speed alerts count
    "nb_alertes_acceleration",   # harsh acceleration count
    "nb_alertes_freinage",       # harsh braking count
    "nb_alertes_geofencing",     # geofence violations
    "nb_alertes_temps",          # driving time violations
    "vitesse_moyenne",           # average speed (km/h)
    "vitesse_max",               # max speed (km/h)
    "score_actuel",              # current risk score
]

PENALTY_WEIGHTS: dict[str, float] = {
    "nb_alertes_vitesse": 5.0,
    "nb_alertes_acceleration": 3.0,
    "nb_alertes_freinage": 3.0,
    "nb_alertes_geofencing": 10.0,
    "nb_alertes_temps": 8.0,
}

RISK_CATEGORIES = {
    "low": (75, 100),
    "medium": (50, 74),
    "high": (25, 49),
    "critical": (0, 24),
}

CATEGORY_THRESHOLDS = [
    (75, "low"),
    (50, "medium"),
    (25, "high"),
    (0, "critical"),
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class DriverFeatures:
    """Telematics feature vector for a single driver."""

    driver_id: str
    nb_alertes_vitesse: int = 0
    nb_alertes_acceleration: int = 0
    nb_alertes_freinage: int = 0
    nb_alertes_geofencing: int = 0
    nb_alertes_temps: int = 0
    vitesse_moyenne: float = 0.0
    vitesse_max: float = 0.0
    score_actuel: float = 100.0

    def to_vector(self) -> list[float]:
        """Convert to feature vector for ML model."""
        return [
            float(self.nb_alertes_vitesse),
            float(self.nb_alertes_acceleration),
            float(self.nb_alertes_freinage),
            float(self.nb_alertes_geofencing),
            float(self.nb_alertes_temps),
            self.vitesse_moyenne,
            self.vitesse_max,
            self.score_actuel,
        ]


@dataclass
class RiskResult:
    """Result of risk scoring for a single driver."""

    driver_id: str
    risk_score: float
    risk_category: str
    feature_values: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Scoring formula
# ---------------------------------------------------------------------------


def compute_risk_score(features: DriverFeatures) -> float:
    """Compute risk score using penalty formula.

    Score = 100 - Sum(penalty_k × nb_infractions_k)
    Clamped to [0, 100].

    Args:
        features: Driver's telematics features.

    Returns:
        Risk score between 0 and 100.
    """
    penalty = 0.0
    penalty += PENALTY_WEIGHTS["nb_alertes_vitesse"] * features.nb_alertes_vitesse
    penalty += PENALTY_WEIGHTS["nb_alertes_acceleration"] * features.nb_alertes_acceleration
    penalty += PENALTY_WEIGHTS["nb_alertes_freinage"] * features.nb_alertes_freinage
    penalty += PENALTY_WEIGHTS["nb_alertes_geofencing"] * features.nb_alertes_geofencing
    penalty += PENALTY_WEIGHTS["nb_alertes_temps"] * features.nb_alertes_temps

    score = 100.0 - penalty
    return max(0.0, min(100.0, score))


def classify_risk(score: float) -> str:
    """Classify a risk score into a category.

    Args:
        score: Risk score (0-100).

    Returns:
        Category string: low, medium, high, or critical.
    """
    for threshold, category in CATEGORY_THRESHOLDS:
        if score >= threshold:
            return category
    return "critical"


def score_driver(features: DriverFeatures) -> RiskResult:
    """Score a single driver and classify risk.

    Args:
        features: Driver telematics features.

    Returns:
        RiskResult with score, category, and feature values.
    """
    risk_score = compute_risk_score(features)
    category = classify_risk(risk_score)

    feature_values = {
        name: val for name, val in zip(FEATURE_NAMES, features.to_vector())
    }

    return RiskResult(
        driver_id=features.driver_id,
        risk_score=risk_score,
        risk_category=category,
        feature_values=feature_values,
    )


def score_drivers_batch(drivers: list[DriverFeatures]) -> list[RiskResult]:
    """Score multiple drivers in batch.

    Args:
        drivers: List of driver feature vectors.

    Returns:
        List of RiskResult objects.
    """
    results = [score_driver(d) for d in drivers]
    logger.info(
        "Batch scored %d drivers: %d low, %d medium, %d high, %d critical",
        len(results),
        sum(1 for r in results if r.risk_category == "low"),
        sum(1 for r in results if r.risk_category == "medium"),
        sum(1 for r in results if r.risk_category == "high"),
        sum(1 for r in results if r.risk_category == "critical"),
    )
    return results


# ---------------------------------------------------------------------------
# RandomForest training
# ---------------------------------------------------------------------------


def extract_features_matrix(drivers: list[DriverFeatures]) -> np.ndarray:
    """Extract feature matrix from driver list.

    Args:
        drivers: List of driver features.

    Returns:
        Feature matrix of shape (n_drivers, 8).
    """
    return np.array([d.to_vector() for d in drivers])


def train_risk_model(
    X: np.ndarray,
    y: np.ndarray,
    n_estimators: int = 50,
    random_state: int = 42,
) -> tuple[RandomForestClassifier, dict]:
    """Train a RandomForest risk classifier.

    Args:
        X: Feature matrix (n, 8).
        y: Labels (risk categories encoded as int).
        n_estimators: Number of trees.
        random_state: Random seed.

    Returns:
        Tuple of (trained model, metrics dict with feature importance).
    """
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X, y)

    # Extract feature importance
    importances = dict(zip(FEATURE_NAMES, model.feature_importances_.tolist()))

    # Training accuracy
    accuracy = float(model.score(X, y))

    metrics = {
        "accuracy": round(accuracy, 4),
        "n_estimators": n_estimators,
        "n_samples": len(X),
        "n_features": X.shape[1],
        "feature_importance": importances,
    }

    logger.info(
        "Trained RF risk model: accuracy=%.3f, n_samples=%d",
        accuracy, len(X),
    )

    return model, metrics


def generate_synthetic_training_data(
    n_samples: int = 500,
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic telematics data for model training.

    Args:
        n_samples: Number of samples.
        random_state: Random seed.

    Returns:
        Tuple of (X, y) where y is encoded category labels.
    """
    rng = np.random.RandomState(random_state)

    X = np.zeros((n_samples, len(FEATURE_NAMES)))
    X[:, 0] = rng.poisson(2, n_samples)   # speed alerts
    X[:, 1] = rng.poisson(1, n_samples)   # acceleration
    X[:, 2] = rng.poisson(1, n_samples)   # braking
    X[:, 3] = rng.poisson(0.5, n_samples) # geofence
    X[:, 4] = rng.poisson(0.3, n_samples) # time
    X[:, 5] = rng.normal(50, 15, n_samples).clip(10, 120)  # avg speed
    X[:, 6] = rng.normal(80, 20, n_samples).clip(30, 180)  # max speed
    X[:, 7] = rng.uniform(20, 100, n_samples)  # current score

    # Compute labels from penalty formula
    y = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        features = DriverFeatures(
            driver_id=f"driver_{i}",
            nb_alertes_vitesse=int(X[i, 0]),
            nb_alertes_acceleration=int(X[i, 1]),
            nb_alertes_freinage=int(X[i, 2]),
            nb_alertes_geofencing=int(X[i, 3]),
            nb_alertes_temps=int(X[i, 4]),
            vitesse_moyenne=X[i, 5],
            vitesse_max=X[i, 6],
            score_actuel=X[i, 7],
        )
        score = compute_risk_score(features)
        category = classify_risk(score)
        y[i] = {"low": 0, "medium": 1, "high": 2, "critical": 3}[category]

    return X, y
