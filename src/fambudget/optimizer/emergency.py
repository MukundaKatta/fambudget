"""EmergencyFundPlanner - computes target emergency fund and timeline."""

from __future__ import annotations

from typing import Optional

from fambudget.models import ExpenseCategory, SavingsGoal


# Essential expense categories for emergency fund calculation
ESSENTIAL_CATEGORIES = {
    ExpenseCategory.HOUSING,
    ExpenseCategory.FOOD,
    ExpenseCategory.TRANSPORT,
    ExpenseCategory.UTILITIES,
    ExpenseCategory.INSURANCE,
}


class EmergencyFundPlanner:
    """Plans emergency fund based on the 3-6 month rule.

    Financial experts recommend having 3-6 months of essential expenses
    saved in a liquid, accessible account. The exact target depends on
    job stability, dependents, and other factors.
    """

    def __init__(
        self,
        monthly_essential_expenses: float,
        current_savings: float = 0.0,
        monthly_contribution: float = 0.0,
    ) -> None:
        """Initialize the emergency fund planner.

        Args:
            monthly_essential_expenses: Total monthly essential expenses.
            current_savings: Current emergency fund balance.
            monthly_contribution: Monthly amount being saved toward the fund.
        """
        if monthly_essential_expenses < 0:
            raise ValueError("Monthly expenses cannot be negative")
        self._monthly_expenses = monthly_essential_expenses
        self._current_savings = max(0, current_savings)
        self._monthly_contribution = max(0, monthly_contribution)

    @classmethod
    def from_expense_breakdown(
        cls,
        spending_by_category: dict[ExpenseCategory, float],
        current_savings: float = 0.0,
        monthly_contribution: float = 0.0,
    ) -> "EmergencyFundPlanner":
        """Create planner from a spending breakdown.

        Only counts essential categories (housing, food, transport,
        utilities, insurance) toward the emergency fund target.
        """
        essential_total = sum(
            amount
            for cat, amount in spending_by_category.items()
            if cat in ESSENTIAL_CATEGORIES
        )
        return cls(essential_total, current_savings, monthly_contribution)

    @property
    def target_minimum(self) -> float:
        """Minimum emergency fund target (3 months of essentials)."""
        return self._monthly_expenses * 3

    @property
    def target_maximum(self) -> float:
        """Maximum recommended emergency fund (6 months of essentials)."""
        return self._monthly_expenses * 6

    @property
    def target_recommended(self) -> float:
        """Recommended target (middle ground: 4.5 months)."""
        return self._monthly_expenses * 4.5

    @property
    def current_coverage_months(self) -> float:
        """How many months of expenses the current savings covers."""
        if self._monthly_expenses == 0:
            return float("inf") if self._current_savings > 0 else 0.0
        return self._current_savings / self._monthly_expenses

    @property
    def is_fully_funded(self) -> bool:
        """Whether the emergency fund meets the minimum 3-month target."""
        return self._current_savings >= self.target_minimum

    def months_to_target(
        self, target_months: float = 3.0
    ) -> Optional[float]:
        """Calculate months needed to reach the target.

        Args:
            target_months: Number of months of expenses to target (default 3).

        Returns:
            Months to reach target, or None if no contributions are being made.
        """
        target = self._monthly_expenses * target_months
        remaining = target - self._current_savings

        if remaining <= 0:
            return 0.0
        if self._monthly_contribution <= 0:
            return None
        return remaining / self._monthly_contribution

    def create_savings_goal(self, target_months: float = 3.0) -> SavingsGoal:
        """Create a SavingsGoal for the emergency fund.

        Args:
            target_months: Number of months of expenses to target.

        Returns:
            A SavingsGoal object.
        """
        target = self._monthly_expenses * target_months
        return SavingsGoal(
            name="Emergency Fund",
            target_amount=target,
            current_amount=self._current_savings,
            monthly_contribution=self._monthly_contribution,
            priority=1,  # Emergency fund is always top priority
        )

    def plan(self) -> dict:
        """Generate a complete emergency fund plan.

        Returns:
            Dict with targets, progress, timeline, and recommendations.
        """
        months_to_min = self.months_to_target(3.0)
        months_to_max = self.months_to_target(6.0)

        recommendations = self._generate_recommendations()

        return {
            "monthly_essential_expenses": self._monthly_expenses,
            "current_savings": self._current_savings,
            "monthly_contribution": self._monthly_contribution,
            "target_minimum": self.target_minimum,
            "target_recommended": self.target_recommended,
            "target_maximum": self.target_maximum,
            "current_coverage_months": round(self.current_coverage_months, 1),
            "is_fully_funded": self.is_fully_funded,
            "months_to_minimum": (
                round(months_to_min, 1) if months_to_min is not None else None
            ),
            "months_to_maximum": (
                round(months_to_max, 1) if months_to_max is not None else None
            ),
            "recommendations": recommendations,
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations for the emergency fund."""
        recs: list[str] = []
        coverage = self.current_coverage_months

        if coverage < 1:
            recs.append(
                "Your emergency fund covers less than 1 month of expenses. "
                "This should be your top financial priority."
            )
            if self._monthly_contribution == 0:
                recs.append(
                    "Start by setting aside even a small amount each month. "
                    "Automate the transfer to make it easier."
                )
        elif coverage < 3:
            recs.append(
                f"Your fund covers {coverage:.1f} months. "
                f"Keep building toward the 3-month minimum."
            )
        elif coverage < 6:
            recs.append(
                f"Great progress! You have {coverage:.1f} months covered. "
                f"Consider building to 6 months for maximum security."
            )
        else:
            recs.append(
                f"Excellent! Your emergency fund covers {coverage:.1f} months. "
                f"You can now focus on other financial goals."
            )

        if self._monthly_contribution > 0 and coverage < 6:
            months = self.months_to_target(6.0)
            if months is not None:
                recs.append(
                    f"At ${self._monthly_contribution:,.0f}/month, you'll "
                    f"reach a 6-month fund in {months:.0f} months."
                )

        return recs
