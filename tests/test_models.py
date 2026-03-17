"""Tests for FamBudget data models."""

import pytest
from pydantic import ValidationError

from fambudget.models import (
    Budget,
    Debt,
    Expense,
    ExpenseCategory,
    Income,
    SavingsGoal,
)


class TestExpense:
    def test_create_expense(self):
        expense = Expense(amount=50.0, category=ExpenseCategory.FOOD)
        assert expense.amount == 50.0
        assert expense.category == ExpenseCategory.FOOD
        assert expense.is_recurring is False

    def test_expense_requires_positive_amount(self):
        with pytest.raises(ValidationError):
            Expense(amount=-10.0, category=ExpenseCategory.FOOD)

    def test_expense_zero_amount_invalid(self):
        with pytest.raises(ValidationError):
            Expense(amount=0, category=ExpenseCategory.FOOD)


class TestIncome:
    def test_create_income(self):
        income = Income(amount=5000.0)
        assert income.amount == 5000.0
        assert income.is_monthly is True
        assert income.after_tax is True


class TestBudget:
    def test_create_budget(self):
        budget = Budget(period="2025-01", income=5000.0)
        assert budget.income == 5000.0
        assert budget.allocations == {}

    def test_budget_negative_allocation_fails(self):
        with pytest.raises(ValidationError):
            Budget(
                period="2025-01",
                income=5000.0,
                allocations={"housing": -100},
            )


class TestSavingsGoal:
    def test_remaining(self):
        goal = SavingsGoal(
            name="Vacation", target_amount=3000, current_amount=1000
        )
        assert goal.remaining == 2000.0

    def test_progress_percent(self):
        goal = SavingsGoal(
            name="Vacation", target_amount=1000, current_amount=250
        )
        assert goal.progress_percent == 25.0

    def test_months_to_goal(self):
        goal = SavingsGoal(
            name="Vacation",
            target_amount=3000,
            current_amount=1000,
            monthly_contribution=500,
        )
        assert goal.months_to_goal == 4.0

    def test_months_to_goal_no_contribution(self):
        goal = SavingsGoal(
            name="Vacation", target_amount=3000, current_amount=1000
        )
        assert goal.months_to_goal is None

    def test_already_reached(self):
        goal = SavingsGoal(
            name="Vacation", target_amount=1000, current_amount=1500
        )
        assert goal.remaining == 0.0
        assert goal.months_to_goal == 0.0


class TestDebt:
    def test_create_debt(self):
        debt = Debt(
            name="Credit Card",
            balance=5000,
            interest_rate=0.18,
            minimum_payment=100,
        )
        assert debt.balance == 5000
        assert debt.interest_rate == 0.18

    def test_monthly_interest_rate(self):
        debt = Debt(
            name="Loan", balance=10000, interest_rate=0.12, minimum_payment=200
        )
        assert debt.monthly_interest_rate == pytest.approx(0.01)

    def test_monthly_interest_charge(self):
        debt = Debt(
            name="Loan", balance=10000, interest_rate=0.12, minimum_payment=200
        )
        assert debt.monthly_interest_charge == pytest.approx(100.0)
