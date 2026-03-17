"""Tests for FinancialSimulator."""

import pytest

from fambudget.models import Debt, SavingsGoal
from fambudget.simulator import FinancialSimulator


class TestFinancialSimulator:
    def test_simulate_savings_basic(self):
        sim = FinancialSimulator(
            monthly_income=5000,
            monthly_expenses=4000,
            current_savings=1000,
            annual_return_rate=0.0,  # No returns for simplicity
        )
        result = sim.simulate_savings(12)
        assert result["months"] == 12
        assert result["starting_balance"] == 1000.0
        # $1000/month surplus * 12 months + $1000 starting = $13000
        assert result["ending_balance"] == 13000.0
        assert result["total_contributions"] == 12000.0

    def test_simulate_savings_with_returns(self):
        sim = FinancialSimulator(
            monthly_income=5000,
            monthly_expenses=4000,
            current_savings=10000,
            annual_return_rate=0.12,  # 12% annual
        )
        result = sim.simulate_savings(12)
        # Should earn interest on savings
        assert result["total_interest_earned"] > 0
        assert result["ending_balance"] > 22000  # More than just contributions

    def test_simulate_no_surplus(self):
        sim = FinancialSimulator(
            monthly_income=4000,
            monthly_expenses=4000,
            current_savings=5000,
            annual_return_rate=0.0,
        )
        result = sim.simulate_savings(6)
        assert result["monthly_surplus"] == 0
        assert result["ending_balance"] == 5000.0

    def test_simulate_net_worth_no_debt(self):
        sim = FinancialSimulator(
            monthly_income=5000,
            monthly_expenses=4000,
            current_savings=10000,
            annual_return_rate=0.0,
        )
        result = sim.simulate_net_worth(12, assets=50000)
        # Net worth = savings + assets
        assert result["starting_net_worth"] == 60000.0
        assert result["ending_net_worth"] == 72000.0

    def test_simulate_net_worth_with_debt(self):
        sim = FinancialSimulator(
            monthly_income=5000,
            monthly_expenses=4000,
            current_savings=10000,
            annual_return_rate=0.0,
        )
        debts = [
            Debt(name="Loan", balance=5000, interest_rate=0.06, minimum_payment=200)
        ]
        result = sim.simulate_net_worth(12, debts=debts)
        # Net worth should increase as debt decreases and savings grow
        assert result["ending_net_worth"] > result["starting_net_worth"]

    def test_project_goal_already_reached(self):
        sim = FinancialSimulator(5000, 4000, 0)
        goal = SavingsGoal(
            name="Test", target_amount=1000, current_amount=1500
        )
        result = sim.project_goal_timeline(goal)
        assert result["already_reached"] is True
        assert result["months_to_goal"] == 0

    def test_project_goal_no_contribution(self):
        sim = FinancialSimulator(5000, 4000, 0)
        goal = SavingsGoal(
            name="Test", target_amount=5000, current_amount=1000
        )
        result = sim.project_goal_timeline(goal)
        assert result["months_to_goal"] is None

    def test_project_goal_with_contributions(self):
        sim = FinancialSimulator(5000, 4000, 0, annual_return_rate=0.0)
        goal = SavingsGoal(
            name="Vacation",
            target_amount=3000,
            current_amount=0,
            monthly_contribution=500,
        )
        result = sim.project_goal_timeline(goal)
        assert result["months_to_goal"] == 6  # $3000 / $500 = 6 months

    def test_monthly_balances_length(self):
        sim = FinancialSimulator(5000, 4000, 0)
        result = sim.simulate_savings(12)
        assert len(result["monthly_balances"]) == 13  # 0 through 12
