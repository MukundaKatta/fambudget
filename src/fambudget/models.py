"""Pydantic data models for FamBudget."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ExpenseCategory(str, Enum):
    """Expense categories for budget tracking."""

    HOUSING = "housing"
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    ENTERTAINMENT = "entertainment"
    SAVINGS = "savings"


class BudgetRuleCategory(str, Enum):
    """50/30/20 rule categories."""

    NEEDS = "needs"
    WANTS = "wants"
    SAVINGS = "savings"


# Mapping of expense categories to 50/30/20 rule categories
CATEGORY_TO_RULE: dict[ExpenseCategory, BudgetRuleCategory] = {
    ExpenseCategory.HOUSING: BudgetRuleCategory.NEEDS,
    ExpenseCategory.FOOD: BudgetRuleCategory.NEEDS,
    ExpenseCategory.TRANSPORT: BudgetRuleCategory.NEEDS,
    ExpenseCategory.UTILITIES: BudgetRuleCategory.NEEDS,
    ExpenseCategory.INSURANCE: BudgetRuleCategory.NEEDS,
    ExpenseCategory.ENTERTAINMENT: BudgetRuleCategory.WANTS,
    ExpenseCategory.SAVINGS: BudgetRuleCategory.SAVINGS,
}


class DebtStrategy(str, Enum):
    """Debt payoff strategies."""

    SNOWBALL = "snowball"
    AVALANCHE = "avalanche"


class Expense(BaseModel):
    """A single expense entry."""

    amount: float = Field(gt=0, description="Expense amount in dollars")
    category: ExpenseCategory = Field(description="Expense category")
    description: str = Field(default="", description="Description of the expense")
    date: date = Field(default_factory=date.today, description="Date of the expense")
    is_recurring: bool = Field(
        default=False, description="Whether this is a recurring expense"
    )


class Income(BaseModel):
    """Income source."""

    amount: float = Field(gt=0, description="Income amount in dollars")
    source: str = Field(default="salary", description="Source of income")
    is_monthly: bool = Field(default=True, description="Whether this is monthly income")
    after_tax: bool = Field(
        default=True, description="Whether this is after-tax income"
    )


class Budget(BaseModel):
    """A budget plan for a given period."""

    period: str = Field(description="Budget period (e.g., '2025-01', 'annual')")
    income: float = Field(ge=0, description="Total income for the period")
    allocations: dict[str, float] = Field(
        default_factory=dict,
        description="Budget allocations by category",
    )
    goals: list[str] = Field(
        default_factory=list, description="Budget goals for the period"
    )
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("allocations")
    @classmethod
    def validate_allocations_non_negative(cls, v: dict[str, float]) -> dict[str, float]:
        for key, amount in v.items():
            if amount < 0:
                raise ValueError(f"Allocation for '{key}' cannot be negative")
        return v


class SavingsGoal(BaseModel):
    """A savings goal with target and timeline."""

    name: str = Field(description="Name of the savings goal")
    target_amount: float = Field(gt=0, description="Target amount in dollars")
    current_amount: float = Field(
        default=0.0, ge=0, description="Current amount saved"
    )
    monthly_contribution: float = Field(
        default=0.0, ge=0, description="Monthly contribution amount"
    )
    target_date: Optional[date] = Field(
        default=None, description="Target date to reach the goal"
    )
    priority: int = Field(default=1, ge=1, le=5, description="Priority level 1-5")

    @property
    def remaining(self) -> float:
        """Amount still needed to reach the goal."""
        return max(0.0, self.target_amount - self.current_amount)

    @property
    def progress_percent(self) -> float:
        """Progress as a percentage."""
        if self.target_amount == 0:
            return 100.0
        return min(100.0, (self.current_amount / self.target_amount) * 100)

    @property
    def months_to_goal(self) -> Optional[float]:
        """Estimated months to reach the goal at current contribution rate."""
        if self.remaining <= 0:
            return 0.0
        if self.monthly_contribution <= 0:
            return None
        return self.remaining / self.monthly_contribution


class Debt(BaseModel):
    """A debt obligation."""

    name: str = Field(description="Name/description of the debt")
    balance: float = Field(ge=0, description="Current balance in dollars")
    interest_rate: float = Field(
        ge=0, le=1, description="Annual interest rate as decimal (e.g., 0.18 for 18%)"
    )
    minimum_payment: float = Field(
        ge=0, description="Minimum monthly payment in dollars"
    )
    is_revolving: bool = Field(
        default=True, description="Whether this is revolving debt (e.g., credit card)"
    )

    @property
    def monthly_interest_rate(self) -> float:
        """Monthly interest rate."""
        return self.interest_rate / 12

    @property
    def monthly_interest_charge(self) -> float:
        """Monthly interest charge on current balance."""
        return self.balance * self.monthly_interest_rate
