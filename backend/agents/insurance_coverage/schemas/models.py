from pydantic import BaseModel
from typing import Literal, Optional


class Liabilities(BaseModel):
    home_loan_outstanding: float = 0.0
    personal_loan_outstanding: float = 0.0
    car_loan_outstanding: float = 0.0
    credit_card_debt: float = 0.0


class ExistingCoverage(BaseModel):
    term_plan_cover: float = 0.0
    employer_group_cover: float = 0.0
    lic_policy_cover: float = 0.0


class CoverageNeedInput(BaseModel):
    monthly_income: float
    current_age: int
    target_retirement_age: int = 60
    number_of_dependents: int
    liabilities: Liabilities
    education_goal_per_child: float = 0.0


class DIMEBreakdown(BaseModel):
    D_debts: float
    I_income_replacement: float
    M_mortgage: float
    E_education: float
    total_required_coverage: float
    calculation_note: str


class GapAnalysisInput(BaseModel):
    required_coverage: float
    existing_coverage: ExistingCoverage


RiskLevel = Literal[
    "critically_underinsured",
    "moderately_underinsured",
    "adequately_covered",
    "over_insured"
]


class GapAnalysisOutput(BaseModel):
    total_existing_coverage: float
    required_coverage: float
    gap: float
    risk_level: RiskLevel
    risk_explanation: str
    priority_action: str
    handoff_triggered: bool
    handoff_reason: Optional[str] = None
    disclaimer: str