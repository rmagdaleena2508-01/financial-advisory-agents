from pydantic import BaseModel
from ..schemas.models import Debt, ConsolidationLoan


class ConsolidationResult(BaseModel):
    option_label: str
    consolidation_amount: float
    processing_fee_amount: float
    effective_loan_amount: float
    new_monthly_emi: float
    total_interest_under_consolidation: float
    total_interest_current_path: float
    net_savings: float
    months_to_payoff: int
    recommendation: str
    behavioral_warning: str


class ConsolidationInput(BaseModel):
    debts_to_consolidate: list[Debt]
    consolidation_options: list[ConsolidationLoan]
    user_monthly_income: float


class ConsolidationOutput(BaseModel):
    results: list[ConsolidationResult]
    best_option_label: str
    summary: str


def _calculate_emi(principal: float, annual_rate_pct: float, months: int) -> float:
    if annual_rate_pct == 0:
        return principal / months
    r = annual_rate_pct / 100 / 12
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def _total_interest_current(debts: list[Debt]) -> float:
    total = 0.0
    for d in debts:
        total_paid = d.monthly_emi * d.tenure_remaining_months
        total += max(0, total_paid - d.principal_outstanding)
    return round(total, 2)


def _analyze_single_option(
    debts: list[Debt],
    option: ConsolidationLoan,
    income: float
) -> ConsolidationResult:

    total_outstanding = sum(d.principal_outstanding for d in debts)
    fee_amount = total_outstanding * option.processing_fee_pct / 100
    effective_principal = total_outstanding + fee_amount

    new_emi = _calculate_emi(
        effective_principal,
        option.interest_rate_pct,
        option.tenure_months
    )

    total_paid_consolidated = new_emi * option.tenure_months
    total_interest_new = total_paid_consolidated - effective_principal
    total_interest_old = _total_interest_current(debts)

    net_savings = round(total_interest_old - total_interest_new - fee_amount, 2)
    emi_to_income_ratio = (new_emi / income) * 100

    if net_savings > 0:
        recommendation = (
            f"This option saves approximately Rs.{net_savings:,.0f} in interest. "
            f"New EMI is Rs.{new_emi:,.0f}/month "
            f"({emi_to_income_ratio:.1f}% of your income)."
        )
    else:
        recommendation = (
            f"This option does NOT save money — you pay Rs.{abs(net_savings):,.0f} MORE "
            f"than your current path. The processing fee and/or rate makes it unfavorable."
        )

    behavioral_warning = (
        "Consolidation only works if you do NOT accumulate new debt on cleared "
        "credit cards or lines after consolidating. Consider closing or reducing "
        "limits on cleared cards to protect yourself."
    )

    return ConsolidationResult(
        option_label=option.lender_label,
        consolidation_amount=round(total_outstanding, 2),
        processing_fee_amount=round(fee_amount, 2),
        effective_loan_amount=round(effective_principal, 2),
        new_monthly_emi=round(new_emi, 2),
        total_interest_under_consolidation=round(total_interest_new, 2),
        total_interest_current_path=total_interest_old,
        net_savings=net_savings,
        months_to_payoff=option.tenure_months,
        recommendation=recommendation,
        behavioral_warning=behavioral_warning,
    )


def run_consolidation_analyzer(input: ConsolidationInput) -> ConsolidationOutput:
    if not input.debts_to_consolidate:
        raise ValueError("No debts provided for consolidation analysis.")
    if not input.consolidation_options:
        raise ValueError("No consolidation options provided.")

    results = [
        _analyze_single_option(
            input.debts_to_consolidate,
            opt,
            input.user_monthly_income
        )
        for opt in input.consolidation_options
    ]

    best = max(results, key=lambda r: r.net_savings)

    if best.net_savings > 0:
        summary = (
            f"Best option is {best.option_label}, "
            f"saving Rs.{best.net_savings:,.0f}. "
            f"New EMI: Rs.{best.new_monthly_emi:,.0f}/month "
            f"over {best.months_to_payoff} months."
        )
    else:
        summary = (
            "None of the provided options save money compared to your current "
            "repayment path. Continue with your existing strategy or negotiate "
            "better terms before consolidating."
        )

    return ConsolidationOutput(
        results=results,
        best_option_label=best.option_label,
        summary=summary,
    )