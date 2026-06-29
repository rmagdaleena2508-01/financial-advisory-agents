import pytest
from ..tools.debt_payoff_optimizer import run_debt_payoff_optimizer, OptimizerInput
from ..schemas.models import Debt


def make_cc():
    return Debt(
        name="HDFC CC", type="credit_card",
        principal_outstanding=150000, interest_rate_pct=36,
        monthly_emi=7500, tenure_remaining_months=36
    )


def make_pl():
    return Debt(
        name="Bajaj PL", type="personal_loan",
        principal_outstanding=300000, interest_rate_pct=14,
        monthly_emi=12000, tenure_remaining_months=30
    )


def test_avalanche_clears_highest_rate_first():
    result = run_debt_payoff_optimizer(OptimizerInput(
        debts=[make_cc(), make_pl()],
        extra_monthly_payment=5000
    ))
    assert result.avalanche.order_debts_paid[0] == "HDFC CC"


def test_snowball_clears_smallest_balance_first():
    result = run_debt_payoff_optimizer(OptimizerInput(
        debts=[make_pl(), make_cc()],
        extra_monthly_payment=5000
    ))
    assert result.snowball.order_debts_paid[0] == "HDFC CC"


def test_avalanche_saves_more_interest():
    result = run_debt_payoff_optimizer(OptimizerInput(
        debts=[make_cc(), make_pl()],
        extra_monthly_payment=5000
    ))
    assert result.avalanche.total_interest_paid <= result.snowball.total_interest_paid


def test_single_debt_both_strategies_identical():
    result = run_debt_payoff_optimizer(OptimizerInput(
        debts=[make_cc()],
        extra_monthly_payment=0
    ))
    assert result.avalanche.months_to_debt_free == result.snowball.months_to_debt_free


def test_zero_extra_payment_still_works():
    result = run_debt_payoff_optimizer(OptimizerInput(
        debts=[make_cc()],
        extra_monthly_payment=0
    ))
    assert result.avalanche.months_to_debt_free > 0


def test_recommendation_avalanche_with_high_interest():
    result = run_debt_payoff_optimizer(OptimizerInput(
        debts=[make_cc(), make_pl()],
        extra_monthly_payment=10000
    ))
    assert result.recommendation == "avalanche"