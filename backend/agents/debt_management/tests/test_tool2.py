from ..tools.debt_consolidation_analyzer import run_consolidation_analyzer, ConsolidationInput
from ..schemas.models import Debt, ConsolidationLoan


def make_debts():
    return [
        Debt(name="CC1", type="credit_card",
             principal_outstanding=100000, interest_rate_pct=36,
             monthly_emi=5000, tenure_remaining_months=24),
        Debt(name="PL1", type="personal_loan",
             principal_outstanding=200000, interest_rate_pct=18,
             monthly_emi=10000, tenure_remaining_months=24),
    ]


def test_lower_rate_consolidation_saves_money():
    result = run_consolidation_analyzer(ConsolidationInput(
        debts_to_consolidate=make_debts(),
        consolidation_options=[
            ConsolidationLoan(lender_label="Option A",
                              interest_rate_pct=12,
                              tenure_months=30,
                              processing_fee_pct=1.0)
        ],
        user_monthly_income=80000
    ))
    assert result.results[0].net_savings > 0


def test_higher_rate_consolidation_loses_money():
    result = run_consolidation_analyzer(ConsolidationInput(
        debts_to_consolidate=make_debts(),
        consolidation_options=[
            ConsolidationLoan(lender_label="Option B",
                              interest_rate_pct=28,
                              tenure_months=30,
                              processing_fee_pct=2.0)
        ],
        user_monthly_income=80000
    ))
    assert result.results[0].net_savings < 0


def test_best_option_selected_correctly():
    result = run_consolidation_analyzer(ConsolidationInput(
        debts_to_consolidate=make_debts(),
        consolidation_options=[
            ConsolidationLoan(lender_label="Option A",
                              interest_rate_pct=12,
                              tenure_months=30,
                              processing_fee_pct=1.0),
            ConsolidationLoan(lender_label="Option B",
                              interest_rate_pct=10,
                              tenure_months=30,
                              processing_fee_pct=0.5),
        ],
        user_monthly_income=80000
    ))
    assert result.best_option_label == "Option B"


def test_behavioral_warning_always_present():
    result = run_consolidation_analyzer(ConsolidationInput(
        debts_to_consolidate=make_debts(),
        consolidation_options=[
            ConsolidationLoan(lender_label="Option A",
                              interest_rate_pct=12,
                              tenure_months=24,
                              processing_fee_pct=0)
        ],
        user_monthly_income=80000
    ))
    assert len(result.results[0].behavioral_warning) > 0


def test_summary_reflects_no_savings():
    result = run_consolidation_analyzer(ConsolidationInput(
        debts_to_consolidate=make_debts(),
        consolidation_options=[
            ConsolidationLoan(lender_label="Option C",
                              interest_rate_pct=30,
                              tenure_months=24,
                              processing_fee_pct=3.0)
        ],
        user_monthly_income=80000
    ))
    assert "None" in result.summary or "not save" in result.summary