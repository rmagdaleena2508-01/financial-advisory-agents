from pydantic import BaseModel
from typing import Literal, Optional


DebtType = Literal[
    "credit_card",
    "personal_loan",
    "home_loan",
    "car_loan",
    "education_loan",
    "bnpl",
    "other"
]


class Debt(BaseModel):
    name: str
    type: DebtType
    principal_outstanding: float
    interest_rate_pct: float
    monthly_emi: float
    tenure_remaining_months: int


class ConsolidationLoan(BaseModel):
    lender_label: str
    interest_rate_pct: float
    tenure_months: int
    processing_fee_pct: float = 0.0


class CreditProfile(BaseModel):
    current_score: Optional[int] = None
    credit_utilization_pct: float
    missed_payments_last_12m: int
    oldest_account_age_months: int
    hard_inquiries_last_6m: int


class HandoffSignal(BaseModel):
    target_agent: Literal[
        "personal_finance",
        "investment_advisory",
        "wealth_retirement"
    ]
    reason: str
    user_context: str