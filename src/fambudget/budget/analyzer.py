"""BudgetAnalyzer - computes spending ratios vs the 50/30/20 rule."""

from __future__ import annotations

from fambudget.models import (
    CATEGORY_TO_RULE,
    BudgetRuleCategory,
    ExpenseCategory,
)


# The 50/30/20 rule targets
RULE_503020 = {
    BudgetRuleCategory.NEEDS: 0.50,
    BudgetRuleCategory.WANTS: 0.30,
    BudgetRuleCategory.SAVINGS: 0.20,
}


class BudgetAnalyzer:
    """Analyzes spending against the 50/30/20 budgeting rule.

    The 50/30/20 rule:
    - 50% of after-tax income goes to NEEDS (housing, food, transport,
      utilities, insurance)
    - 30% goes to WANTS (entertainment, dining out, hobbies)
    - 20% goes to SAVINGS and debt repayment
    """

    def __init__(self, monthly_income: float) -> None:
        """Initialize with monthly after-tax income.

        Args:
            monthly_income: Monthly after-tax income in dollars.
        """
        if monthly_income <= 0:
            raise ValueError("Monthly income must be positive")
        self._monthly_income = monthly_income

    @property
    def monthly_income(self) -> float:
        return self._monthly_income

    def ideal_allocations(self) -> dict[BudgetRuleCategory, float]:
        """Return ideal dollar allocations according to 50/30/20."""
        return {
            cat: self._monthly_income * ratio
            for cat, ratio in RULE_503020.items()
        }

    def analyze(
        self, spending_by_category: dict[ExpenseCategory, float]
    ) -> dict[str, object]:
        """Analyze spending against the 50/30/20 rule.

        Args:
            spending_by_category: Actual spending per expense category.

        Returns:
            Analysis dict with actual vs ideal ratios and recommendations.
        """
        # Aggregate spending into 50/30/20 categories
        actual_by_rule: dict[BudgetRuleCategory, float] = {
            BudgetRuleCategory.NEEDS: 0.0,
            BudgetRuleCategory.WANTS: 0.0,
            BudgetRuleCategory.SAVINGS: 0.0,
        }

        for cat, amount in spending_by_category.items():
            rule_cat = CATEGORY_TO_RULE.get(cat, BudgetRuleCategory.WANTS)
            actual_by_rule[rule_cat] += amount

        total_spending = sum(actual_by_rule.values())
        ideal = self.ideal_allocations()

        # Compute ratios
        actual_ratios = {}
        deviations = {}
        for rule_cat in BudgetRuleCategory:
            actual = actual_by_rule[rule_cat]
            if self._monthly_income > 0:
                actual_ratios[rule_cat] = actual / self._monthly_income
            else:
                actual_ratios[rule_cat] = 0.0
            deviations[rule_cat] = actual - ideal[rule_cat]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            actual_by_rule, ideal, deviations
        )

        return {
            "monthly_income": self._monthly_income,
            "total_spending": total_spending,
            "spending_rate": total_spending / self._monthly_income if self._monthly_income > 0 else 0,
            "actual_amounts": dict(actual_by_rule),
            "ideal_amounts": dict(ideal),
            "actual_ratios": dict(actual_ratios),
            "ideal_ratios": dict(RULE_503020),
            "deviations": dict(deviations),
            "recommendations": recommendations,
            "is_within_budget": total_spending <= self._monthly_income,
        }

    def _generate_recommendations(
        self,
        actual: dict[BudgetRuleCategory, float],
        ideal: dict[BudgetRuleCategory, float],
        deviations: dict[BudgetRuleCategory, float],
    ) -> list[str]:
        """Generate actionable recommendations based on spending analysis."""
        recs: list[str] = []

        # Check needs
        needs_dev = deviations[BudgetRuleCategory.NEEDS]
        if needs_dev > 0:
            excess = needs_dev
            recs.append(
                f"Your needs spending exceeds the 50% target by ${excess:,.2f}. "
                f"Consider reducing housing costs or finding cheaper alternatives "
                f"for essentials."
            )

        # Check wants
        wants_dev = deviations[BudgetRuleCategory.WANTS]
        if wants_dev > 0:
            excess = wants_dev
            recs.append(
                f"Your wants spending exceeds the 30% target by ${excess:,.2f}. "
                f"Look for entertainment and discretionary expenses to cut."
            )

        # Check savings
        savings_dev = deviations[BudgetRuleCategory.SAVINGS]
        if savings_dev < 0:
            shortfall = abs(savings_dev)
            recs.append(
                f"You're saving ${shortfall:,.2f} less than the 20% target. "
                f"Try to increase savings by automating transfers."
            )

        # Overall budget check
        total = sum(actual.values())
        if total > self._monthly_income:
            overspend = total - self._monthly_income
            recs.append(
                f"You're overspending by ${overspend:,.2f} per month. "
                f"This is unsustainable -- prioritize cutting expenses."
            )

        if not recs:
            recs.append(
                "Your spending is well-aligned with the 50/30/20 rule. "
                "Keep up the good work!"
            )

        return recs
