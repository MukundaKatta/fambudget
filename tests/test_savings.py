"""Tests for SavingsOptimizer."""

import pytest

from fambudget.models import ExpenseCategory
from fambudget.optimizer.savings import SavingsOptimizer


class TestSavingsOptimizer:
    def test_find_opportunities_over_benchmark(self):
        optimizer = SavingsOptimizer(5000.0)
        spending = {
            ExpenseCategory.HOUSING: 2000.0,  # 40% vs 28% benchmark
            ExpenseCategory.FOOD: 500.0,      # 10% = benchmark
            ExpenseCategory.ENTERTAINMENT: 500.0,  # 10% vs 5% benchmark
        }
        opportunities = optimizer.find_savings_opportunities(spending)
        assert len(opportunities) >= 1
        # Housing should be the biggest opportunity
        assert opportunities[0]["category"] == "housing"

    def test_no_opportunities_when_under_benchmarks(self):
        optimizer = SavingsOptimizer(10000.0)
        spending = {
            ExpenseCategory.HOUSING: 1000.0,  # 10% vs 28%
            ExpenseCategory.FOOD: 500.0,      # 5% vs 10%
        }
        opportunities = optimizer.find_savings_opportunities(spending)
        assert len(opportunities) == 0

    def test_total_potential_savings(self):
        optimizer = SavingsOptimizer(5000.0)
        spending = {
            ExpenseCategory.HOUSING: 2000.0,  # $600 over benchmark (28% = $1400)
            ExpenseCategory.ENTERTAINMENT: 500.0,  # $250 over benchmark (5% = $250)
        }
        total = optimizer.total_potential_savings(spending)
        assert total > 0

    def test_suggest_savings_rate(self):
        optimizer = SavingsOptimizer(5000.0)
        spending = {
            ExpenseCategory.SAVINGS: 500.0,  # 10% current
            ExpenseCategory.HOUSING: 2000.0,
        }
        suggestion = optimizer.suggest_savings_rate(spending)
        assert suggestion["current_rate"] == pytest.approx(0.10)
        assert suggestion["target_rate"] == 0.20

    def test_savings_not_suggested_for_cutting(self):
        optimizer = SavingsOptimizer(5000.0)
        spending = {
            ExpenseCategory.SAVINGS: 2000.0,  # High savings is good!
        }
        opportunities = optimizer.find_savings_opportunities(spending)
        # Savings category should never appear as a cut target
        assert all(o["category"] != "savings" for o in opportunities)

    def test_invalid_income(self):
        with pytest.raises(ValueError):
            SavingsOptimizer(0)
