"""DebtPayoffOptimizer - snowball and avalanche debt payoff strategies."""

from __future__ import annotations

import copy

from fambudget.models import Debt, DebtStrategy


class DebtPayoffOptimizer:
    """Optimizes debt payoff using snowball or avalanche strategies.

    Snowball: Pay minimums on all debts, put extra money toward the
    smallest balance first. Provides psychological wins.

    Avalanche: Pay minimums on all debts, put extra money toward the
    highest interest rate first. Saves the most money on interest.
    """

    def __init__(self, debts: list[Debt], extra_payment: float = 0.0) -> None:
        """Initialize with debts and optional extra monthly payment.

        Args:
            debts: List of current debts.
            extra_payment: Extra monthly amount available for debt payoff
                beyond minimum payments.
        """
        self._debts = debts
        self._extra_payment = extra_payment

    @property
    def total_debt(self) -> float:
        """Total outstanding debt balance."""
        return sum(d.balance for d in self._debts)

    @property
    def total_minimum_payments(self) -> float:
        """Total minimum monthly payments across all debts."""
        return sum(d.minimum_payment for d in self._debts)

    @property
    def total_monthly_interest(self) -> float:
        """Total monthly interest charges across all debts."""
        return sum(d.monthly_interest_charge for d in self._debts)

    def payoff_plan(
        self, strategy: DebtStrategy = DebtStrategy.AVALANCHE
    ) -> dict:
        """Generate a complete debt payoff plan.

        Args:
            strategy: SNOWBALL (smallest balance first) or
                AVALANCHE (highest interest first).

        Returns:
            Dict with payoff schedule, total interest, and months to debt-free.
        """
        if not self._debts:
            return {
                "strategy": strategy.value,
                "months_to_payoff": 0,
                "total_interest_paid": 0.0,
                "total_paid": 0.0,
                "payoff_order": [],
                "monthly_schedule": [],
            }

        # Work with copies to avoid mutating originals
        working_debts = [
            {"name": d.name, "balance": d.balance, "rate": d.interest_rate,
             "monthly_rate": d.monthly_interest_rate, "min_payment": d.minimum_payment}
            for d in self._debts
        ]

        # Sort based on strategy
        if strategy == DebtStrategy.SNOWBALL:
            working_debts.sort(key=lambda d: d["balance"])
        else:  # AVALANCHE
            working_debts.sort(key=lambda d: d["rate"], reverse=True)

        payoff_order: list[dict] = []
        monthly_schedule: list[dict] = []
        total_interest = 0.0
        total_paid = 0.0
        month = 0
        max_months = 600  # 50-year safety cap

        while any(d["balance"] > 0.01 for d in working_debts) and month < max_months:
            month += 1
            month_interest = 0.0
            month_principal = 0.0
            extra_remaining = self._extra_payment

            # Apply interest to all debts
            for debt in working_debts:
                if debt["balance"] > 0:
                    interest = debt["balance"] * debt["monthly_rate"]
                    debt["balance"] += interest
                    month_interest += interest

            # Pay minimums on all debts
            for debt in working_debts:
                if debt["balance"] > 0:
                    payment = min(debt["min_payment"], debt["balance"])
                    debt["balance"] -= payment
                    month_principal += payment
                    total_paid += payment

            # Apply extra payment to target debt (first in sorted order with balance)
            for debt in working_debts:
                if debt["balance"] > 0 and extra_remaining > 0:
                    payment = min(extra_remaining, debt["balance"])
                    debt["balance"] -= payment
                    extra_remaining -= payment
                    month_principal += payment
                    total_paid += payment

                    # Check if this debt is now paid off
                    if debt["balance"] <= 0.01:
                        debt["balance"] = 0
                        payoff_order.append({
                            "name": debt["name"],
                            "paid_off_month": month,
                        })
                        # Snowball/avalanche: freed minimum goes to next debt
                        self._extra_payment += debt["min_payment"]
                    break  # Extra only goes to the target debt

            total_interest += month_interest

            monthly_schedule.append({
                "month": month,
                "interest_paid": round(month_interest, 2),
                "principal_paid": round(month_principal, 2),
                "remaining_balance": round(
                    sum(d["balance"] for d in working_debts), 2
                ),
            })

        return {
            "strategy": strategy.value,
            "months_to_payoff": month,
            "total_interest_paid": round(total_interest, 2),
            "total_paid": round(total_paid, 2),
            "payoff_order": payoff_order,
            "monthly_schedule": monthly_schedule,
        }

    def compare_strategies(self) -> dict:
        """Compare snowball vs avalanche strategies.

        Returns:
            Comparison dict with both plans and the savings difference.
        """
        # Reset extra payment for fair comparison
        original_extra = self._extra_payment
        self._extra_payment = original_extra
        snowball = self.payoff_plan(DebtStrategy.SNOWBALL)

        self._extra_payment = original_extra
        avalanche = self.payoff_plan(DebtStrategy.AVALANCHE)

        interest_saved = snowball["total_interest_paid"] - avalanche["total_interest_paid"]
        months_saved = snowball["months_to_payoff"] - avalanche["months_to_payoff"]

        return {
            "snowball": snowball,
            "avalanche": avalanche,
            "interest_saved_with_avalanche": round(interest_saved, 2),
            "months_saved_with_avalanche": months_saved,
            "recommendation": (
                "The avalanche method saves you more money on interest, "
                "but the snowball method provides quicker wins for motivation."
                if interest_saved > 0
                else "Both strategies perform similarly for your debts."
            ),
        }
