"""Tests for BudgetPlanner."""

import pytest

from fambudget.budget.planner import BudgetPlanner


class TestBudgetPlanner:
    def test_create_monthly_budget(self):
        planner = BudgetPlanner(5000.0)
        budget = planner.create_monthly_budget("2025-01")
        assert budget.period == "2025-01"
        assert budget.income == 5000.0
        assert len(budget.allocations) > 0

    def test_monthly_allocations_sum(self):
        planner = BudgetPlanner(5000.0)
        budget = planner.create_monthly_budget("2025-01")
        total_allocated = sum(budget.allocations.values())
        # Default allocations: 30% housing + 10% food + 5% transport +
        # 3% utilities + 2% insurance + 30% entertainment + 20% savings = 100%
        assert total_allocated == pytest.approx(5000.0)

    def test_create_annual_budget(self):
        planner = BudgetPlanner(5000.0)
        budget = planner.create_annual_budget(2025)
        assert budget.period == "2025"
        assert budget.income == 60000.0

    def test_annual_allocations_are_12x_monthly(self):
        planner = BudgetPlanner(5000.0)
        monthly = planner.create_monthly_budget("2025-01")
        annual = planner.create_annual_budget(2025)
        for cat in monthly.allocations:
            assert annual.allocations[cat] == pytest.approx(
                monthly.allocations[cat] * 12
            )

    def test_custom_allocations(self):
        planner = BudgetPlanner(5000.0)
        custom = {"housing": 1800, "food": 600, "savings": 1000}
        budget = planner.create_monthly_budget("2025-01", custom_allocations=custom)
        assert budget.allocations["housing"] == 1800

    def test_custom_goals(self):
        planner = BudgetPlanner(5000.0)
        goals = ["Save for vacation", "Pay off credit card"]
        budget = planner.create_monthly_budget("2025-01", goals=goals)
        assert budget.goals == goals

    def test_adjust_for_income_change(self):
        planner = BudgetPlanner(5000.0)
        budget = planner.create_monthly_budget("2025-01")
        adjusted = planner.adjust_for_income_change(6000.0, budget)
        assert adjusted.income == 6000.0
        # All allocations should scale by 6000/5000 = 1.2
        for cat in budget.allocations:
            assert adjusted.allocations[cat] == pytest.approx(
                budget.allocations[cat] * 1.2
            )

    def test_invalid_income(self):
        with pytest.raises(ValueError):
            BudgetPlanner(0)
