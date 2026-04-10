"""Tests for Markowitz portfolio optimizer (SOTREG M5)."""
from __future__ import annotations

import pytest

from app.services.sotreg.portfolio_optimizer import (
    compute_efficient_frontier,
    compute_minimum_variance_portfolio,
    compute_portfolio_optimization,
)


class TestPortfolioOptimization:
    """Verify Markowitz mean-variance optimization."""

    def test_weights_sum_to_one(self) -> None:
        """Portfolio weights must sum to 1.0."""
        result = compute_portfolio_optimization(
            expected_returns=[0.10, 0.15, 0.08],
            covariance_matrix=[
                [0.04, 0.01, 0.005],
                [0.01, 0.09, 0.01],
                [0.005, 0.01, 0.02],
            ],
        )
        assert abs(sum(result["weights"]) - 1.0) < 0.01

    def test_all_weights_non_negative(self) -> None:
        """No short selling — all weights >= 0."""
        result = compute_portfolio_optimization(
            expected_returns=[0.10, 0.15, 0.08],
            covariance_matrix=[
                [0.04, 0.01, 0.005],
                [0.01, 0.09, 0.01],
                [0.005, 0.01, 0.02],
            ],
        )
        for w in result["weights"]:
            assert w >= -0.001  # Small tolerance

    def test_single_asset(self) -> None:
        """Single asset → weight = 1.0."""
        result = compute_portfolio_optimization(
            expected_returns=[0.10],
            covariance_matrix=[[0.04]],
        )
        assert abs(result["weights"][0] - 1.0) < 0.01

    def test_risk_aversion_effect(self) -> None:
        """Higher risk aversion → more conservative portfolio (lower risk)."""
        low_ra = compute_portfolio_optimization(
            expected_returns=[0.10, 0.20],
            covariance_matrix=[[0.02, 0.005], [0.005, 0.10]],
            risk_aversion=0.5,
        )
        high_ra = compute_portfolio_optimization(
            expected_returns=[0.10, 0.20],
            covariance_matrix=[[0.02, 0.005], [0.005, 0.10]],
            risk_aversion=5.0,
        )
        assert high_ra["portfolio_std"] <= low_ra["portfolio_std"] + 0.01

    def test_sharpe_ratio_computed(self) -> None:
        """Sharpe ratio should be present."""
        result = compute_portfolio_optimization(
            expected_returns=[0.10, 0.15],
            covariance_matrix=[[0.04, 0.01], [0.01, 0.09]],
        )
        assert "sharpe_ratio" in result

    def test_technology_names(self) -> None:
        """Technology names should be returned."""
        result = compute_portfolio_optimization(
            expected_returns=[0.10, 0.15],
            covariance_matrix=[[0.04, 0.01], [0.01, 0.09]],
            technology_names=["diesel", "electric"],
        )
        assert result["technology_names"] == ["diesel", "electric"]


class TestEfficientFrontier:
    """Verify efficient frontier computation."""

    def test_frontier_multiple_points(self) -> None:
        """Frontier should have n_points portfolios."""
        result = compute_efficient_frontier(
            expected_returns=[0.08, 0.12, 0.15],
            covariance_matrix=[
                [0.02, 0.005, 0.002],
                [0.005, 0.04, 0.01],
                [0.002, 0.01, 0.06],
            ],
            n_points=10,
        )
        assert len(result["frontier"]) >= 5  # At least 5 valid points

    def test_frontier_monotone_risk_return(self) -> None:
        """Higher return → higher or equal risk on frontier."""
        result = compute_efficient_frontier(
            expected_returns=[0.05, 0.10, 0.20],
            covariance_matrix=[
                [0.01, 0.002, 0.001],
                [0.002, 0.04, 0.005],
                [0.001, 0.005, 0.10],
            ],
            n_points=15,
        )
        frontier = result["frontier"]
        for i in range(1, len(frontier)):
            if frontier[i]["expected_return"] > frontier[i - 1]["expected_return"]:
                assert frontier[i]["risk"] >= frontier[i - 1]["risk"] - 0.01

    def test_min_and_max_portfolios(self) -> None:
        """Should identify min-risk and max-return portfolios."""
        result = compute_efficient_frontier(
            expected_returns=[0.08, 0.15],
            covariance_matrix=[[0.02, 0.005], [0.005, 0.06]],
        )
        assert "min_risk_portfolio" in result
        assert "max_return_portfolio" in result


class TestMinimumVariance:
    """Verify global minimum variance portfolio."""

    def test_min_variance_weights_sum_one(self) -> None:
        """Min variance weights sum to 1."""
        result = compute_minimum_variance_portfolio(
            covariance_matrix=[[0.04, 0.01], [0.01, 0.09]],
        )
        assert abs(sum(result["weights"]) - 1.0) < 0.01

    def test_min_variance_favors_low_variance(self) -> None:
        """Should allocate more to lower-variance asset."""
        result = compute_minimum_variance_portfolio(
            covariance_matrix=[[0.01, 0.0], [0.0, 0.10]],
        )
        # Asset 0 has much lower variance → should get more weight
        assert result["weights"][0] > result["weights"][1]
