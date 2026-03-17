# FamBudget

Family Budget Optimizer -- smart budgeting with real financial planning rules.

## Features

- **Expense Tracking**: Categorize spending across housing, food, transport,
  utilities, insurance, entertainment, and savings.
- **Budget Analysis**: Compare your spending against the 50/30/20 rule
  (50% needs, 30% wants, 20% savings/debt).
- **Budget Planning**: Create monthly and annual budgets with goals.
- **Savings Optimization**: Find areas to cut spending and maximize savings.
- **Debt Payoff**: Snowball and avalanche strategies for debt elimination.
- **Emergency Fund Planning**: Compute target (3-6 months of expenses) and
  timeline to reach it.
- **Financial Simulation**: Project future net worth and savings growth.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Add an expense
fambudget add-expense --category housing --amount 1500 --description "Rent"

# View budget analysis with 50/30/20 breakdown
fambudget analyze

# Create a monthly budget plan
fambudget plan --income 5000

# Find savings opportunities
fambudget optimize

# Plan debt payoff
fambudget debt --strategy avalanche

# Plan emergency fund
fambudget emergency --monthly-expenses 3000

# Run a financial simulation
fambudget simulate --months 12

# Generate a full report
fambudget report
```

## Financial Rules

- **50/30/20 Rule**: 50% of after-tax income to needs, 30% to wants, 20% to
  savings and debt repayment.
- **Emergency Fund**: 3-6 months of essential expenses.
- **Debt Snowball**: Pay minimums on all debts, extra toward smallest balance.
- **Debt Avalanche**: Pay minimums on all debts, extra toward highest interest rate.

## Project Structure

```
src/fambudget/
  cli.py           - Command-line interface (Click)
  models.py        - Pydantic data models
  report.py        - Financial reporting
  simulator.py     - Financial projection simulator
  budget/
    tracker.py     - ExpenseTracker (categorized spending)
    analyzer.py    - BudgetAnalyzer (50/30/20 rule)
    planner.py     - BudgetPlanner (monthly/annual budgets)
  optimizer/
    savings.py     - SavingsOptimizer (cut spending)
    debt.py        - DebtPayoffOptimizer (snowball/avalanche)
    emergency.py   - EmergencyFundPlanner (3-6mo target)
```
