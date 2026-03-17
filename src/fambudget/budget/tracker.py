"""ExpenseTracker - categorizes and tracks spending."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Optional

from fambudget.models import Expense, ExpenseCategory


class ExpenseTracker:
    """Tracks and categorizes household spending.

    Categories: housing, food, transport, utilities, insurance,
    entertainment, savings.
    """

    def __init__(self) -> None:
        self._expenses: list[Expense] = []

    @property
    def expenses(self) -> list[Expense]:
        """All tracked expenses."""
        return list(self._expenses)

    def add_expense(
        self,
        amount: float,
        category: ExpenseCategory,
        description: str = "",
        expense_date: Optional[date] = None,
        is_recurring: bool = False,
    ) -> Expense:
        """Add a new expense.

        Args:
            amount: Expense amount in dollars.
            category: Expense category.
            description: Description of the expense.
            expense_date: Date of the expense (defaults to today).
            is_recurring: Whether this is a recurring expense.

        Returns:
            The created Expense.
        """
        expense = Expense(
            amount=amount,
            category=category,
            description=description,
            date=expense_date or date.today(),
            is_recurring=is_recurring,
        )
        self._expenses.append(expense)
        return expense

    def total_spending(self) -> float:
        """Total spending across all categories."""
        return sum(e.amount for e in self._expenses)

    def spending_by_category(self) -> dict[ExpenseCategory, float]:
        """Total spending broken down by category."""
        totals: dict[ExpenseCategory, float] = defaultdict(float)
        for expense in self._expenses:
            totals[expense.category] += expense.amount
        return dict(totals)

    def spending_for_period(
        self, start_date: date, end_date: date
    ) -> list[Expense]:
        """Get expenses within a date range."""
        return [
            e for e in self._expenses if start_date <= e.date <= end_date
        ]

    def recurring_expenses(self) -> list[Expense]:
        """Get all recurring expenses."""
        return [e for e in self._expenses if e.is_recurring]

    def monthly_recurring_total(self) -> float:
        """Total monthly cost of all recurring expenses."""
        return sum(e.amount for e in self._expenses if e.is_recurring)

    def top_expenses(self, n: int = 5) -> list[Expense]:
        """Get the top N expenses by amount."""
        return sorted(self._expenses, key=lambda e: e.amount, reverse=True)[:n]

    def category_percentages(self) -> dict[ExpenseCategory, float]:
        """Spending per category as a percentage of total."""
        total = self.total_spending()
        if total == 0:
            return {}
        by_cat = self.spending_by_category()
        return {cat: (amt / total) * 100 for cat, amt in by_cat.items()}

    def clear(self) -> None:
        """Clear all tracked expenses."""
        self._expenses.clear()

    def load_expenses(self, expenses: list[Expense]) -> None:
        """Load a list of expenses."""
        self._expenses.extend(expenses)
