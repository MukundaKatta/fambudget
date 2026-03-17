"""Tests for EmergencyFundPlanner."""

import pytest

from fambudget.models import ExpenseCategory
from fambudget.optimizer.emergency import EmergencyFundPlanner


class TestEmergencyFundPlanner:
    def test_targets(self):
        planner = EmergencyFundPlanner(3000)
        assert planner.target_minimum == 9000.0   # 3 months
        assert planner.target_maximum == 18000.0   # 6 months
        assert planner.target_recommended == 13500.0  # 4.5 months

    def test_coverage_months(self):
        planner = EmergencyFundPlanner(3000, current_savings=6000)
        assert planner.current_coverage_months == 2.0

    def test_is_fully_funded(self):
        planner = EmergencyFundPlanner(3000, current_savings=9000)
        assert planner.is_fully_funded is True

    def test_not_fully_funded(self):
        planner = EmergencyFundPlanner(3000, current_savings=5000)
        assert planner.is_fully_funded is False

    def test_months_to_target(self):
        planner = EmergencyFundPlanner(
            3000, current_savings=0, monthly_contribution=1000
        )
        # Need $9000, contributing $1000/month = 9 months
        assert planner.months_to_target(3.0) == 9.0

    def test_months_to_target_already_met(self):
        planner = EmergencyFundPlanner(
            3000, current_savings=10000, monthly_contribution=500
        )
        assert planner.months_to_target(3.0) == 0.0

    def test_months_to_target_no_contribution(self):
        planner = EmergencyFundPlanner(3000, current_savings=1000)
        assert planner.months_to_target(3.0) is None

    def test_from_expense_breakdown(self):
        spending = {
            ExpenseCategory.HOUSING: 1500,
            ExpenseCategory.FOOD: 500,
            ExpenseCategory.TRANSPORT: 300,
            ExpenseCategory.UTILITIES: 200,
            ExpenseCategory.INSURANCE: 200,
            ExpenseCategory.ENTERTAINMENT: 500,  # Not essential
        }
        planner = EmergencyFundPlanner.from_expense_breakdown(spending)
        # Essential = 1500 + 500 + 300 + 200 + 200 = 2700
        assert planner.target_minimum == 8100.0  # 2700 * 3

    def test_create_savings_goal(self):
        planner = EmergencyFundPlanner(3000, current_savings=3000, monthly_contribution=500)
        goal = planner.create_savings_goal(3.0)
        assert goal.name == "Emergency Fund"
        assert goal.target_amount == 9000.0
        assert goal.current_amount == 3000.0
        assert goal.priority == 1

    def test_plan_output(self):
        planner = EmergencyFundPlanner(3000, current_savings=3000, monthly_contribution=500)
        plan = planner.plan()
        assert "monthly_essential_expenses" in plan
        assert "target_minimum" in plan
        assert "is_fully_funded" in plan
        assert "recommendations" in plan
        assert len(plan["recommendations"]) > 0

    def test_negative_expenses_raises(self):
        with pytest.raises(ValueError):
            EmergencyFundPlanner(-100)
