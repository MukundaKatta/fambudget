"""Command-line interface for FamBudget."""

from __future__ import annotations

from typing import Optional

import click
from rich.console import Console

from fambudget.budget.analyzer import BudgetAnalyzer
from fambudget.budget.planner import BudgetPlanner
from fambudget.budget.tracker import ExpenseTracker
from fambudget.models import Debt, DebtStrategy, ExpenseCategory
from fambudget.optimizer.debt import DebtPayoffOptimizer
from fambudget.optimizer.emergency import EmergencyFundPlanner
from fambudget.optimizer.savings import SavingsOptimizer
from fambudget.report import BudgetReporter
from fambudget.simulator import FinancialSimulator

console = Console()
tracker = ExpenseTracker()
reporter = BudgetReporter(console)


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """FamBudget - Family Budget Optimizer.

    Smart budgeting with real financial planning rules.
    """
    pass


@main.command("add-expense")
@click.option(
    "--category",
    type=click.Choice([c.value for c in ExpenseCategory]),
    required=True,
    help="Expense category.",
)
@click.option("--amount", type=float, required=True, help="Expense amount.")
@click.option("--description", default="", help="Description.")
@click.option("--recurring", is_flag=True, help="Mark as recurring.")
def add_expense(category: str, amount: float, description: str, recurring: bool) -> None:
    """Add an expense."""
    expense = tracker.add_expense(
        amount=amount,
        category=ExpenseCategory(category),
        description=description,
        is_recurring=recurring,
    )
    console.print(
        f"[green]Added ${expense.amount:,.2f} to {expense.category.value}[/green]"
    )


@main.command()
@click.option("--income", type=float, required=True, help="Monthly after-tax income.")
def analyze(income: float) -> None:
    """Analyze spending against the 50/30/20 rule."""
    spending = tracker.spending_by_category()
    if not spending:
        console.print("[yellow]No expenses tracked yet. Use add-expense first.[/yellow]")
        return

    reporter.display_spending_breakdown(spending, income)

    analyzer = BudgetAnalyzer(income)
    analysis = analyzer.analyze(spending)
    reporter.display_503020_analysis(analysis)


@main.command()
@click.option("--income", type=float, required=True, help="Monthly after-tax income.")
@click.option("--month", default=None, help="Month (e.g., 2025-01). Defaults to current.")
def plan(income: float, month: Optional[str]) -> None:
    """Create a monthly budget plan."""
    from datetime import date

    if month is None:
        today = date.today()
        month = f"{today.year}-{today.month:02d}"

    planner = BudgetPlanner(income)
    budget = planner.create_monthly_budget(month)

    console.print(f"\n[bold]Budget Plan for {budget.period}[/bold]")
    console.print(f"Income: ${budget.income:,.2f}\n")

    from rich.table import Table

    table = Table(title="Allocations", show_header=True)
    table.add_column("Category", style="cyan")
    table.add_column("Amount", justify="right", style="green")

    for cat, amount in budget.allocations.items():
        table.add_row(cat.capitalize(), f"${amount:,.2f}")

    console.print(table)

    console.print("\n[bold]Goals:[/bold]")
    for goal in budget.goals:
        console.print(f"  - {goal}")


@main.command()
@click.option("--income", type=float, required=True, help="Monthly after-tax income.")
def optimize(income: float) -> None:
    """Find savings opportunities."""
    spending = tracker.spending_by_category()
    if not spending:
        console.print("[yellow]No expenses tracked yet. Use add-expense first.[/yellow]")
        return

    optimizer = SavingsOptimizer(income)
    opportunities = optimizer.find_savings_opportunities(spending)
    reporter.display_savings_opportunities(opportunities)

    suggestion = optimizer.suggest_savings_rate(spending)
    console.print(
        f"\n[cyan]Current savings rate:[/cyan] {suggestion['current_rate']:.1%}"
    )
    console.print(
        f"[cyan]Suggested savings rate:[/cyan] {suggestion['suggested_rate']:.1%}"
    )


@main.command()
@click.option("--monthly-expenses", type=float, required=True, help="Monthly essential expenses.")
@click.option("--current-savings", type=float, default=0, help="Current emergency savings.")
@click.option("--contribution", type=float, default=0, help="Monthly contribution.")
def emergency(monthly_expenses: float, current_savings: float, contribution: float) -> None:
    """Plan your emergency fund."""
    planner = EmergencyFundPlanner(monthly_expenses, current_savings, contribution)
    plan = planner.plan()
    reporter.display_emergency_fund_plan(plan)


@main.command()
@click.option("--income", type=float, required=True, help="Monthly after-tax income.")
@click.option("--expenses", type=float, required=True, help="Monthly total expenses.")
@click.option("--savings", type=float, default=0, help="Current savings balance.")
@click.option("--months", type=int, default=12, help="Months to simulate.")
def simulate(income: float, expenses: float, savings: float, months: int) -> None:
    """Run a financial simulation."""
    sim = FinancialSimulator(income, expenses, savings)
    result = sim.simulate_savings(months)
    reporter.display_simulation(result)


@main.command()
@click.option("--income", type=float, required=True, help="Monthly after-tax income.")
def report(income: float) -> None:
    """Generate a full budget report."""
    spending = tracker.spending_by_category()
    if not spending:
        console.print("[yellow]No expenses tracked yet. Use add-expense first.[/yellow]")
        return

    reporter.display_spending_breakdown(spending, income)

    analyzer = BudgetAnalyzer(income)
    analysis = analyzer.analyze(spending)
    reporter.display_503020_analysis(analysis)

    optimizer = SavingsOptimizer(income)
    opportunities = optimizer.find_savings_opportunities(spending)
    reporter.display_savings_opportunities(opportunities)


if __name__ == "__main__":
    main()
