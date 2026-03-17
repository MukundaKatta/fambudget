"""Tests for ExpenseTracker."""

from datetime import date

from fambudget.budget.tracker import ExpenseTracker
from fambudget.models import ExpenseCategory


class TestExpenseTracker:
    def test_add_expense(self):
        tracker = ExpenseTracker()
        expense = tracker.add_expense(100.0, ExpenseCategory.FOOD, "Groceries")
        assert expense.amount == 100.0
        assert expense.category == ExpenseCategory.FOOD
        assert len(tracker.expenses) == 1

    def test_total_spending(self):
        tracker = ExpenseTracker()
        tracker.add_expense(1500, ExpenseCategory.HOUSING, "Rent")
        tracker.add_expense(400, ExpenseCategory.FOOD, "Groceries")
        tracker.add_expense(100, ExpenseCategory.ENTERTAINMENT, "Movies")
        assert tracker.total_spending() == 2000.0

    def test_spending_by_category(self):
        tracker = ExpenseTracker()
        tracker.add_expense(1500, ExpenseCategory.HOUSING)
        tracker.add_expense(200, ExpenseCategory.FOOD)
        tracker.add_expense(300, ExpenseCategory.FOOD)
        by_cat = tracker.spending_by_category()
        assert by_cat[ExpenseCategory.HOUSING] == 1500.0
        assert by_cat[ExpenseCategory.FOOD] == 500.0

    def test_spending_for_period(self):
        tracker = ExpenseTracker()
        tracker.add_expense(
            100, ExpenseCategory.FOOD, expense_date=date(2025, 1, 15)
        )
        tracker.add_expense(
            200, ExpenseCategory.FOOD, expense_date=date(2025, 2, 15)
        )
        tracker.add_expense(
            300, ExpenseCategory.FOOD, expense_date=date(2025, 3, 15)
        )
        period = tracker.spending_for_period(date(2025, 1, 1), date(2025, 1, 31))
        assert len(period) == 1
        assert period[0].amount == 100.0

    def test_recurring_expenses(self):
        tracker = ExpenseTracker()
        tracker.add_expense(1500, ExpenseCategory.HOUSING, is_recurring=True)
        tracker.add_expense(50, ExpenseCategory.ENTERTAINMENT)
        assert len(tracker.recurring_expenses()) == 1
        assert tracker.monthly_recurring_total() == 1500.0

    def test_top_expenses(self):
        tracker = ExpenseTracker()
        tracker.add_expense(100, ExpenseCategory.FOOD)
        tracker.add_expense(1500, ExpenseCategory.HOUSING)
        tracker.add_expense(50, ExpenseCategory.ENTERTAINMENT)
        top = tracker.top_expenses(2)
        assert len(top) == 2
        assert top[0].amount == 1500.0

    def test_category_percentages(self):
        tracker = ExpenseTracker()
        tracker.add_expense(500, ExpenseCategory.HOUSING)
        tracker.add_expense(500, ExpenseCategory.FOOD)
        pcts = tracker.category_percentages()
        assert pcts[ExpenseCategory.HOUSING] == 50.0
        assert pcts[ExpenseCategory.FOOD] == 50.0

    def test_clear(self):
        tracker = ExpenseTracker()
        tracker.add_expense(100, ExpenseCategory.FOOD)
        tracker.clear()
        assert len(tracker.expenses) == 0

    def test_empty_tracker(self):
        tracker = ExpenseTracker()
        assert tracker.total_spending() == 0.0
        assert tracker.spending_by_category() == {}
        assert tracker.category_percentages() == {}
