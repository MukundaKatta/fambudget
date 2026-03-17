"""Tests for BudgetAnalyzer."""

import pytest

from fambudget.budget.analyzer import BudgetAnalyzer
from fambudget.models import BudgetRuleCategory, ExpenseCategory


class TestBudgetAnalyzer:
    def test_ideal_allocations(self):
        analyzer = BudgetAnalyzer(5000.0)
        ideal = analyzer.ideal_allocations()
        assert ideal[BudgetRuleCategory.NEEDS] == 2500.0
        assert ideal[BudgetRuleCategory.WANTS] == 1500.0
        assert ideal[BudgetRuleCategory.SAVINGS] == 1000.0

    def test_perfect_budget(self):
        analyzer = BudgetAnalyzer(5000.0)
        spending = {
            ExpenseCategory.HOUSING: 1500.0,
            ExpenseCategory.FOOD: 500.0,
            ExpenseCategory.TRANSPORT: 300.0,
            ExpenseCategory.UTILITIES: 100.0,
            ExpenseCategory.INSURANCE: 100.0,
            ExpenseCategory.ENTERTAINMENT: 1500.0,
            ExpenseCategory.SAVINGS: 1000.0,
        }
        analysis = analyzer.analyze(spending)
        assert analysis["is_within_budget"]
        # Needs = 2500, Wants = 1500, Savings = 1000 -> perfect 50/30/20
        assert analysis["actual_ratios"][BudgetRuleCategory.NEEDS] == pytest.approx(0.50)
        assert analysis["actual_ratios"][BudgetRuleCategory.WANTS] == pytest.approx(0.30)
        assert analysis["actual_ratios"][BudgetRuleCategory.SAVINGS] == pytest.approx(0.20)

    def test_overspending_detected(self):
        analyzer = BudgetAnalyzer(5000.0)
        spending = {
            ExpenseCategory.HOUSING: 3000.0,  # Too high
            ExpenseCategory.FOOD: 1000.0,
            ExpenseCategory.ENTERTAINMENT: 2000.0,  # Too high
        }
        analysis = analyzer.analyze(spending)
        assert not analysis["is_within_budget"]
        assert analysis["spending_rate"] > 1.0

    def test_savings_shortfall_recommendation(self):
        analyzer = BudgetAnalyzer(5000.0)
        spending = {
            ExpenseCategory.HOUSING: 2500.0,
            ExpenseCategory.ENTERTAINMENT: 1500.0,
            ExpenseCategory.SAVINGS: 500.0,  # Below 20% target
        }
        analysis = analyzer.analyze(spending)
        recs = analysis["recommendations"]
        assert any("saving" in r.lower() or "savings" in r.lower() for r in recs)

    def test_invalid_income(self):
        with pytest.raises(ValueError):
            BudgetAnalyzer(0)

    def test_well_aligned_budget_gets_praise(self):
        analyzer = BudgetAnalyzer(5000.0)
        spending = {
            ExpenseCategory.HOUSING: 1500.0,
            ExpenseCategory.FOOD: 500.0,
            ExpenseCategory.TRANSPORT: 300.0,
            ExpenseCategory.UTILITIES: 100.0,
            ExpenseCategory.INSURANCE: 100.0,
            ExpenseCategory.ENTERTAINMENT: 1500.0,
            ExpenseCategory.SAVINGS: 1000.0,
        }
        analysis = analyzer.analyze(spending)
        recs = analysis["recommendations"]
        assert any("good work" in r.lower() or "well-aligned" in r.lower() for r in recs)
