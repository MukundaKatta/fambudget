"""Financial reporting for FamBudget."""

from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fambudget.models import BudgetRuleCategory, ExpenseCategory


class BudgetReporter:
    """Generates and displays budget reports using Rich."""

    def __init__(self, console: Optional[Console] = None) -> None:
        self._console = console or Console()

    def display_spending_breakdown(
        self,
        spending_by_category: dict[ExpenseCategory, float],
        monthly_income: float,
    ) -> None:
        """Display a spending breakdown table."""
        table = Table(title="Spending Breakdown", show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Amount", justify="right", style="green")
        table.add_column("% of Income", justify="right", style="yellow")

        total = 0.0
        for cat in ExpenseCategory:
            amount = spending_by_category.get(cat, 0.0)
            total += amount
            pct = (amount / monthly_income * 100) if monthly_income > 0 else 0
            table.add_row(cat.value.capitalize(), f"${amount:,.2f}", f"{pct:.1f}%")

        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]${total:,.2f}[/bold]",
            f"[bold]{(total / monthly_income * 100) if monthly_income > 0 else 0:.1f}%[/bold]",
        )

        self._console.print(table)

    def display_503020_analysis(self, analysis: dict) -> None:
        """Display the 50/30/20 analysis."""
        self._console.print()
        self._console.print(
            Panel("[bold]50/30/20 Budget Analysis[/bold]", style="blue")
        )

        table = Table(show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Actual", justify="right", style="green")
        table.add_column("Target", justify="right", style="yellow")
        table.add_column("Difference", justify="right")

        for rule_cat in BudgetRuleCategory:
            actual = analysis["actual_amounts"].get(rule_cat, 0)
            ideal = analysis["ideal_amounts"].get(rule_cat, 0)
            actual_pct = analysis["actual_ratios"].get(rule_cat, 0) * 100
            ideal_pct = analysis["ideal_ratios"].get(rule_cat, 0) * 100
            diff = actual - ideal

            diff_style = "green" if diff <= 0 else "red"
            if rule_cat == BudgetRuleCategory.SAVINGS:
                diff_style = "green" if diff >= 0 else "red"

            table.add_row(
                f"{rule_cat.value.capitalize()} ({ideal_pct:.0f}%)",
                f"${actual:,.2f} ({actual_pct:.1f}%)",
                f"${ideal:,.2f}",
                f"[{diff_style}]${diff:+,.2f}[/{diff_style}]",
            )

        self._console.print(table)

        # Recommendations
        if analysis.get("recommendations"):
            self._console.print()
            for rec in analysis["recommendations"]:
                self._console.print(f"  [yellow]>[/yellow] {rec}")

    def display_savings_opportunities(self, opportunities: list[dict]) -> None:
        """Display savings opportunities."""
        if not opportunities:
            self._console.print("[green]No areas of overspending identified![/green]")
            return

        table = Table(title="Savings Opportunities", show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Current", justify="right", style="red")
        table.add_column("Benchmark", justify="right", style="green")
        table.add_column("Potential Savings", justify="right", style="yellow")

        total_savings = 0.0
        for opp in opportunities:
            total_savings += opp["potential_savings"]
            table.add_row(
                opp["category"].capitalize(),
                f"${opp['current_spending']:,.2f}",
                f"${opp['benchmark_spending']:,.2f}",
                f"${opp['potential_savings']:,.2f}",
            )

        table.add_row(
            "[bold]Total[/bold]", "", "",
            f"[bold]${total_savings:,.2f}/month[/bold]",
        )

        self._console.print(table)

        self._console.print()
        for opp in opportunities:
            self._console.print(f"  [yellow]>[/yellow] {opp['recommendation']}")

    def display_emergency_fund_plan(self, plan: dict) -> None:
        """Display emergency fund plan."""
        self._console.print()
        self._console.print(
            Panel("[bold]Emergency Fund Plan[/bold]", style="blue")
        )

        table = Table(show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")

        table.add_row(
            "Monthly Essential Expenses",
            f"${plan['monthly_essential_expenses']:,.2f}",
        )
        table.add_row("Current Savings", f"${plan['current_savings']:,.2f}")
        table.add_row(
            "Coverage",
            f"{plan['current_coverage_months']} months",
        )
        table.add_row("Target (3 months)", f"${plan['target_minimum']:,.2f}")
        table.add_row("Target (6 months)", f"${plan['target_maximum']:,.2f}")

        status = "[green]Funded[/green]" if plan["is_fully_funded"] else "[red]Below Target[/red]"
        table.add_row("Status", status)

        if plan["months_to_minimum"] is not None and not plan["is_fully_funded"]:
            table.add_row(
                "Months to 3-month target",
                str(plan["months_to_minimum"]),
            )
        if plan["months_to_maximum"] is not None:
            table.add_row(
                "Months to 6-month target",
                str(plan["months_to_maximum"]),
            )

        self._console.print(table)

        if plan.get("recommendations"):
            self._console.print()
            for rec in plan["recommendations"]:
                self._console.print(f"  [yellow]>[/yellow] {rec}")

    def display_simulation(self, sim_result: dict) -> None:
        """Display simulation results summary."""
        self._console.print()
        self._console.print(
            Panel("[bold]Financial Projection[/bold]", style="blue")
        )

        table = Table(show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")

        table.add_row("Projection Period", f"{sim_result['months']} months")
        table.add_row("Monthly Surplus", f"${sim_result['monthly_surplus']:,.2f}")
        table.add_row("Starting Balance", f"${sim_result['starting_balance']:,.2f}")
        table.add_row("Ending Balance", f"${sim_result['ending_balance']:,.2f}")
        table.add_row(
            "Total Contributions",
            f"${sim_result['total_contributions']:,.2f}",
        )
        table.add_row(
            "Interest Earned",
            f"${sim_result['total_interest_earned']:,.2f}",
        )

        self._console.print(table)
