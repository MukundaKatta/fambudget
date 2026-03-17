"""BudgetPlanner - creates monthly and annual budgets with goals."""

from __future__ import annotations

from datetime import datetime

from fambudget.models import Budget, BudgetRuleCategory, ExpenseCategory, CATEGORY_TO_RULE


# Default allocation percentages within the NEEDS category
NEEDS_BREAKDOWN = {
    ExpenseCategory.HOUSING: 0.30,     # 30% of total income
    ExpenseCategory.FOOD: 0.10,        # 10%
    ExpenseCategory.TRANSPORT: 0.05,   # 5%
    ExpenseCategory.UTILITIES: 0.03,   # 3%
    ExpenseCategory.INSURANCE: 0.02,   # 2%
}

# Default allocation percentages within WANTS
WANTS_BREAKDOWN = {
    ExpenseCategory.ENTERTAINMENT: 0.30,  # 30% of total income
}

# Default allocation percentages within SAVINGS
SAVINGS_BREAKDOWN = {
    ExpenseCategory.SAVINGS: 0.20,  # 20% of total income
}


class BudgetPlanner:
    """Creates monthly and annual budgets with goals.

    Uses the 50/30/20 rule as the default framework, with customizable
    allocations per category.
    """

    def __init__(self, monthly_income: float) -> None:
        if monthly_income <= 0:
            raise ValueError("Monthly income must be positive")
        self._monthly_income = monthly_income

    @property
    def monthly_income(self) -> float:
        return self._monthly_income

    def create_monthly_budget(
        self,
        month: str,
        custom_allocations: dict[str, float] | None = None,
        goals: list[str] | None = None,
    ) -> Budget:
        """Create a monthly budget.

        Args:
            month: Month identifier (e.g., '2025-01').
            custom_allocations: Override default allocations.
            goals: Budget goals for the month.

        Returns:
            A Budget object with allocations.
        """
        if custom_allocations is not None:
            allocations = custom_allocations
        else:
            allocations = self._default_monthly_allocations()

        default_goals = goals or self._default_goals()

        return Budget(
            period=month,
            income=self._monthly_income,
            allocations=allocations,
            goals=default_goals,
        )

    def create_annual_budget(
        self,
        year: int,
        custom_allocations: dict[str, float] | None = None,
        goals: list[str] | None = None,
    ) -> Budget:
        """Create an annual budget.

        Args:
            year: The budget year.
            custom_allocations: Override default allocations (annual amounts).
            goals: Budget goals for the year.

        Returns:
            A Budget object with annual allocations.
        """
        annual_income = self._monthly_income * 12

        if custom_allocations is not None:
            allocations = custom_allocations
        else:
            monthly = self._default_monthly_allocations()
            allocations = {cat: amt * 12 for cat, amt in monthly.items()}

        default_goals = goals or [
            f"Save ${annual_income * 0.20:,.0f} (20% of annual income)",
            "Build or maintain 3-6 month emergency fund",
            "Review and reduce recurring subscriptions",
            "Increase retirement contributions if possible",
        ]

        return Budget(
            period=str(year),
            income=annual_income,
            allocations=allocations,
            goals=default_goals,
        )

    def _default_monthly_allocations(self) -> dict[str, float]:
        """Generate default monthly allocations based on 50/30/20."""
        allocations: dict[str, float] = {}
        for cat, pct in NEEDS_BREAKDOWN.items():
            allocations[cat.value] = self._monthly_income * pct
        for cat, pct in WANTS_BREAKDOWN.items():
            allocations[cat.value] = self._monthly_income * pct
        for cat, pct in SAVINGS_BREAKDOWN.items():
            allocations[cat.value] = self._monthly_income * pct
        return allocations

    def _default_goals(self) -> list[str]:
        """Generate default monthly goals."""
        savings_target = self._monthly_income * 0.20
        return [
            f"Save at least ${savings_target:,.0f} this month",
            "Track all expenses daily",
            "Stay within budget for entertainment",
        ]

    def adjust_for_income_change(
        self, new_income: float, budget: Budget
    ) -> Budget:
        """Adjust an existing budget for a change in income.

        Maintains the same percentage allocations.
        """
        if new_income <= 0:
            raise ValueError("New income must be positive")

        ratio = new_income / self._monthly_income
        new_allocations = {
            cat: amt * ratio for cat, amt in budget.allocations.items()
        }

        return Budget(
            period=budget.period,
            income=new_income,
            allocations=new_allocations,
            goals=budget.goals,
        )
