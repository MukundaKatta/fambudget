"""SavingsOptimizer - finds areas to cut spending and maximize savings."""

from __future__ import annotations

from fambudget.models import (
    CATEGORY_TO_RULE,
    BudgetRuleCategory,
    Expense,
    ExpenseCategory,
)


# Typical spending benchmarks as percentage of income
SPENDING_BENCHMARKS: dict[ExpenseCategory, float] = {
    ExpenseCategory.HOUSING: 0.28,       # HUD recommends max 28-30%
    ExpenseCategory.FOOD: 0.10,          # USDA moderate plan ~10%
    ExpenseCategory.TRANSPORT: 0.10,     # ~10% is typical
    ExpenseCategory.UTILITIES: 0.05,     # ~5% is typical
    ExpenseCategory.INSURANCE: 0.05,     # ~5% is typical
    ExpenseCategory.ENTERTAINMENT: 0.05, # ~5% is reasonable
    ExpenseCategory.SAVINGS: 0.20,       # 20% target from 50/30/20
}


class SavingsOptimizer:
    """Finds areas to cut spending and maximize savings.

    Compares actual spending against benchmarks and identifies the
    categories with the most savings potential.
    """

    def __init__(self, monthly_income: float) -> None:
        if monthly_income <= 0:
            raise ValueError("Monthly income must be positive")
        self._monthly_income = monthly_income

    def find_savings_opportunities(
        self,
        spending_by_category: dict[ExpenseCategory, float],
    ) -> list[dict]:
        """Identify categories where spending can be reduced.

        Args:
            spending_by_category: Current monthly spending per category.

        Returns:
            List of savings opportunities sorted by potential savings amount.
        """
        opportunities: list[dict] = []

        for category, actual in spending_by_category.items():
            if category == ExpenseCategory.SAVINGS:
                continue  # Don't suggest cutting savings

            benchmark = SPENDING_BENCHMARKS.get(category, 0.10)
            benchmark_amount = self._monthly_income * benchmark

            if actual > benchmark_amount:
                potential_savings = actual - benchmark_amount
                opportunities.append({
                    "category": category.value,
                    "current_spending": actual,
                    "benchmark_spending": benchmark_amount,
                    "potential_savings": potential_savings,
                    "percent_over": ((actual - benchmark_amount) / benchmark_amount) * 100,
                    "recommendation": self._get_recommendation(category, potential_savings),
                })

        # Sort by potential savings (highest first)
        opportunities.sort(key=lambda x: x["potential_savings"], reverse=True)
        return opportunities

    def total_potential_savings(
        self,
        spending_by_category: dict[ExpenseCategory, float],
    ) -> float:
        """Calculate total potential monthly savings."""
        opportunities = self.find_savings_opportunities(spending_by_category)
        return sum(o["potential_savings"] for o in opportunities)

    def suggest_savings_rate(
        self,
        spending_by_category: dict[ExpenseCategory, float],
    ) -> dict:
        """Suggest an optimal savings rate based on current spending.

        Returns:
            Dict with current and suggested savings rates and amounts.
        """
        current_savings = spending_by_category.get(ExpenseCategory.SAVINGS, 0)
        current_rate = current_savings / self._monthly_income if self._monthly_income > 0 else 0
        potential = self.total_potential_savings(spending_by_category)

        suggested_rate = min(0.30, current_rate + (potential / self._monthly_income))
        suggested_amount = self._monthly_income * suggested_rate

        return {
            "current_savings": current_savings,
            "current_rate": current_rate,
            "suggested_rate": suggested_rate,
            "suggested_amount": suggested_amount,
            "additional_savings_possible": potential,
            "target_rate": 0.20,  # 50/30/20 rule target
        }

    def _get_recommendation(self, category: ExpenseCategory, amount: float) -> str:
        """Generate a specific recommendation for a spending category."""
        recs: dict[ExpenseCategory, str] = {
            ExpenseCategory.HOUSING: (
                f"Consider downsizing, getting a roommate, or refinancing "
                f"to save ~${amount:,.0f}/month on housing."
            ),
            ExpenseCategory.FOOD: (
                f"Try meal planning, cooking at home more, and reducing "
                f"dining out to save ~${amount:,.0f}/month on food."
            ),
            ExpenseCategory.TRANSPORT: (
                f"Consider carpooling, public transit, or a more fuel-efficient "
                f"vehicle to save ~${amount:,.0f}/month on transport."
            ),
            ExpenseCategory.UTILITIES: (
                f"Reduce utility costs by adjusting thermostat, using LED bulbs, "
                f"and fixing leaks to save ~${amount:,.0f}/month."
            ),
            ExpenseCategory.INSURANCE: (
                f"Shop around for insurance quotes and bundle policies "
                f"to save ~${amount:,.0f}/month."
            ),
            ExpenseCategory.ENTERTAINMENT: (
                f"Cut streaming subscriptions, find free activities, and "
                f"set entertainment limits to save ~${amount:,.0f}/month."
            ),
        }
        return recs.get(
            category,
            f"Look for ways to reduce spending by ~${amount:,.0f}/month.",
        )
