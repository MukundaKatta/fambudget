"""Tests for DebtPayoffOptimizer."""

import pytest

from fambudget.models import Debt, DebtStrategy
from fambudget.optimizer.debt import DebtPayoffOptimizer


def _sample_debts() -> list[Debt]:
    return [
        Debt(
            name="Credit Card",
            balance=5000,
            interest_rate=0.18,
            minimum_payment=100,
        ),
        Debt(
            name="Car Loan",
            balance=15000,
            interest_rate=0.06,
            minimum_payment=300,
        ),
        Debt(
            name="Student Loan",
            balance=10000,
            interest_rate=0.05,
            minimum_payment=150,
        ),
    ]


class TestDebtPayoffOptimizer:
    def test_total_debt(self):
        optimizer = DebtPayoffOptimizer(_sample_debts())
        assert optimizer.total_debt == 30000

    def test_total_minimum_payments(self):
        optimizer = DebtPayoffOptimizer(_sample_debts())
        assert optimizer.total_minimum_payments == 550

    def test_snowball_plan(self):
        optimizer = DebtPayoffOptimizer(_sample_debts(), extra_payment=200)
        plan = optimizer.payoff_plan(DebtStrategy.SNOWBALL)
        assert plan["strategy"] == "snowball"
        assert plan["months_to_payoff"] > 0
        assert plan["total_interest_paid"] > 0
        # Snowball pays smallest balance first (Credit Card = $5000)
        assert plan["payoff_order"][0]["name"] == "Credit Card"

    def test_avalanche_plan(self):
        optimizer = DebtPayoffOptimizer(_sample_debts(), extra_payment=200)
        plan = optimizer.payoff_plan(DebtStrategy.AVALANCHE)
        assert plan["strategy"] == "avalanche"
        assert plan["months_to_payoff"] > 0
        # Avalanche pays highest interest first (Credit Card = 18%)
        assert plan["payoff_order"][0]["name"] == "Credit Card"

    def test_avalanche_saves_interest(self):
        debts = [
            Debt(name="High Rate", balance=5000, interest_rate=0.24, minimum_payment=100),
            Debt(name="Low Rate", balance=5000, interest_rate=0.06, minimum_payment=100),
        ]
        optimizer = DebtPayoffOptimizer(debts, extra_payment=200)
        comparison = optimizer.compare_strategies()
        # Avalanche should generally save money on interest
        assert comparison["interest_saved_with_avalanche"] >= 0

    def test_no_debts(self):
        optimizer = DebtPayoffOptimizer([])
        plan = optimizer.payoff_plan()
        assert plan["months_to_payoff"] == 0
        assert plan["total_interest_paid"] == 0.0

    def test_compare_strategies(self):
        optimizer = DebtPayoffOptimizer(_sample_debts(), extra_payment=200)
        comparison = optimizer.compare_strategies()
        assert "snowball" in comparison
        assert "avalanche" in comparison
        assert "recommendation" in comparison

    def test_monthly_schedule_has_entries(self):
        optimizer = DebtPayoffOptimizer(_sample_debts(), extra_payment=200)
        plan = optimizer.payoff_plan()
        assert len(plan["monthly_schedule"]) > 0
        assert plan["monthly_schedule"][0]["month"] == 1
