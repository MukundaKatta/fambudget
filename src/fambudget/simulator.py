"""Financial simulator - projects future net worth and savings growth."""

from __future__ import annotations

import numpy as np

from fambudget.models import Debt, ExpenseCategory, SavingsGoal


class FinancialSimulator:
    """Simulates financial projections over time.

    Projects savings growth, debt paydown, and net worth using
    monthly timesteps with optional interest/return rates.
    """

    def __init__(
        self,
        monthly_income: float,
        monthly_expenses: float,
        current_savings: float = 0.0,
        annual_return_rate: float = 0.05,
    ) -> None:
        """Initialize the simulator.

        Args:
            monthly_income: Monthly after-tax income.
            monthly_expenses: Total monthly expenses (excluding extra savings).
            current_savings: Starting savings balance.
            annual_return_rate: Expected annual return on savings (default 5%).
        """
        self._monthly_income = monthly_income
        self._monthly_expenses = monthly_expenses
        self._current_savings = current_savings
        self._annual_return_rate = annual_return_rate
        self._monthly_return_rate = (1 + annual_return_rate) ** (1 / 12) - 1

    def simulate_savings(self, months: int) -> dict:
        """Simulate savings growth over a period.

        Args:
            months: Number of months to simulate.

        Returns:
            Dict with monthly projections and summary statistics.
        """
        monthly_surplus = self._monthly_income - self._monthly_expenses
        balances = np.zeros(months + 1)
        contributions = np.zeros(months + 1)
        interest_earned = np.zeros(months + 1)

        balances[0] = self._current_savings
        total_contributions = 0.0
        total_interest = 0.0

        for m in range(1, months + 1):
            # Add monthly surplus
            contribution = max(0, monthly_surplus)
            total_contributions += contribution

            # Calculate interest on previous balance
            interest = balances[m - 1] * self._monthly_return_rate
            total_interest += interest

            balances[m] = balances[m - 1] + contribution + interest
            contributions[m] = total_contributions
            interest_earned[m] = total_interest

        return {
            "months": months,
            "monthly_surplus": round(monthly_surplus, 2),
            "starting_balance": round(self._current_savings, 2),
            "ending_balance": round(float(balances[-1]), 2),
            "total_contributions": round(total_contributions, 2),
            "total_interest_earned": round(total_interest, 2),
            "annual_return_rate": self._annual_return_rate,
            "monthly_balances": [round(float(b), 2) for b in balances],
        }

    def simulate_net_worth(
        self,
        months: int,
        debts: list[Debt] | None = None,
        assets: float = 0.0,
    ) -> dict:
        """Simulate net worth projection.

        Args:
            months: Number of months to simulate.
            debts: Current debts (interest accrues, minimums paid).
            assets: Non-liquid assets (e.g., home equity).

        Returns:
            Dict with monthly net worth projections.
        """
        savings_sim = self.simulate_savings(months)
        monthly_surplus = max(0, self._monthly_income - self._monthly_expenses)

        # Simulate debt paydown
        debt_balances = np.zeros(months + 1)
        if debts:
            total_debt = sum(d.balance for d in debts)
            debt_balances[0] = total_debt
            total_min_payments = sum(d.minimum_payment for d in debts)
            avg_monthly_rate = (
                np.mean([d.monthly_interest_rate for d in debts]) if debts else 0
            )

            for m in range(1, months + 1):
                interest = debt_balances[m - 1] * avg_monthly_rate
                payment = min(total_min_payments, debt_balances[m - 1] + interest)
                debt_balances[m] = max(0, debt_balances[m - 1] + interest - payment)

        # Net worth = savings + assets - debts
        net_worth = [
            round(float(savings_sim["monthly_balances"][m]) + assets - float(debt_balances[m]), 2)
            for m in range(months + 1)
        ]

        return {
            "months": months,
            "starting_net_worth": net_worth[0],
            "ending_net_worth": net_worth[-1],
            "net_worth_change": round(net_worth[-1] - net_worth[0], 2),
            "monthly_net_worth": net_worth,
            "savings_balances": savings_sim["monthly_balances"],
            "debt_balances": [round(float(d), 2) for d in debt_balances],
        }

    def project_goal_timeline(self, goal: SavingsGoal) -> dict:
        """Project when a savings goal will be reached.

        Args:
            goal: The savings goal to project.

        Returns:
            Dict with projected timeline and growth.
        """
        if goal.remaining <= 0:
            return {
                "goal_name": goal.name,
                "already_reached": True,
                "months_to_goal": 0,
            }

        monthly_contribution = goal.monthly_contribution
        if monthly_contribution <= 0:
            return {
                "goal_name": goal.name,
                "already_reached": False,
                "months_to_goal": None,
                "message": "No monthly contribution set. Goal cannot be reached.",
            }

        balance = goal.current_amount
        month = 0
        max_months = 600

        while balance < goal.target_amount and month < max_months:
            month += 1
            interest = balance * self._monthly_return_rate
            balance += monthly_contribution + interest

        return {
            "goal_name": goal.name,
            "already_reached": False,
            "months_to_goal": month if month < max_months else None,
            "projected_balance": round(balance, 2),
            "target_amount": goal.target_amount,
            "monthly_contribution": monthly_contribution,
        }
