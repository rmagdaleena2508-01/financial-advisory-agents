from ..tools.credit_score_planner import run_credit_score_planner
from ..schemas.models import CreditProfile


def test_high_utilization_marked_critical():
    profile = CreditProfile(
        current_score=620,
        credit_utilization_pct=80,
        missed_payments_last_12m=0,
        oldest_account_age_months=36,
        hard_inquiries_last_6m=1
    )
    plan = run_credit_score_planner(profile)
    utilization_impactor = next(
        i for i in plan.impactors if "utilization" in i.factor.lower()
    )
    assert utilization_impactor.impact_level == "critical"


def test_missed_payments_sorted_first():
    profile = CreditProfile(
        current_score=580,
        credit_utilization_pct=40,
        missed_payments_last_12m=4,
        oldest_account_age_months=24,
        hard_inquiries_last_6m=2
    )
    plan = run_credit_score_planner(profile)
    assert plan.impactors[0].impact_level == "critical"


def test_quick_wins_present_for_high_utilization():
    profile = CreditProfile(
        current_score=640,
        credit_utilization_pct=75,
        missed_payments_last_12m=0,
        oldest_account_age_months=48,
        hard_inquiries_last_6m=0
    )
    plan = run_credit_score_planner(profile)
    assert len(plan.quick_wins) > 0


def test_disclaimer_always_present():
    profile = CreditProfile(
        current_score=750,
        credit_utilization_pct=15,
        missed_payments_last_12m=0,
        oldest_account_age_months=84,
        hard_inquiries_last_6m=0
    )
    plan = run_credit_score_planner(profile)
    assert len(plan.disclaimer) > 0


def test_unknown_score_does_not_crash():
    profile = CreditProfile(
        current_score=None,
        credit_utilization_pct=50,
        missed_payments_last_12m=1,
        oldest_account_age_months=18,
        hard_inquiries_last_6m=2
    )
    plan = run_credit_score_planner(profile)
    assert plan is not None


def test_excellent_score_no_critical_flags():
    profile = CreditProfile(
        current_score=820,
        credit_utilization_pct=8,
        missed_payments_last_12m=0,
        oldest_account_age_months=96,
        hard_inquiries_last_6m=0
    )
    plan = run_credit_score_planner(profile)
    critical = [i for i in plan.impactors if i.impact_level == "critical"]
    assert len(critical) == 0