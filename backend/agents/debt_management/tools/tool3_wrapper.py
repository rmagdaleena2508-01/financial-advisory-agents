from crewai.tools import tool
from .credit_score_planner import run_credit_score_planner
from ..schemas.models import CreditProfile
import json


@tool("Credit Score Improvement Planner")
def credit_score_planner_tool(
    current_score: int,
    credit_utilization_pct: float,
    missed_payments_last_12m: int,
    oldest_account_age_months: int,
    hard_inquiries_last_6m: int
) -> str:
    """
    Builds a personalized CIBIL credit score improvement plan.

    Use this tool when:
    - User asks how to improve their CIBIL or credit score
    - User wants to know why their score is low
    - User is planning to apply for a loan and wants better eligibility
    - User asks about credit utilization, missed payments, or hard inquiries

    Does NOT fetch live scores. Works from user-provided information only.

    Args:
        current_score: User's CIBIL score (300-900). Pass 0 if unknown.
        credit_utilization_pct: Percentage of total credit limit currently used (0-100)
        missed_payments_last_12m: Number of missed EMI or credit payments in last 12 months
        oldest_account_age_months: Age of oldest credit account in months
        hard_inquiries_last_6m: Number of loan or card applications in last 6 months

    Returns:
        JSON with prioritized actions, timeline, and projected score improvement.
    """
    try:
        profile = CreditProfile(
            current_score=current_score if current_score > 0 else None,
            credit_utilization_pct=credit_utilization_pct,
            missed_payments_last_12m=missed_payments_last_12m,
            oldest_account_age_months=oldest_account_age_months,
            hard_inquiries_last_6m=hard_inquiries_last_6m
        )
        plan = run_credit_score_planner(profile)
        return json.dumps({
            "current_band": plan.estimated_current_band,
            "target_band": plan.target_band,
            "projected_score_12_months": plan.projected_score_range,
            "top_impactors": [
                {
                    "factor": i.factor,
                    "status": i.current_status,
                    "priority": i.impact_level,
                    "action": i.action,
                    "expected_gain": i.estimated_score_gain,
                }
                for i in plan.impactors[:3]
            ],
            "quick_wins": plan.quick_wins,
            "six_month_actions": plan.six_month_actions,
            "twelve_month_actions": plan.twelve_month_actions,
            "disclaimer": plan.disclaimer,
        }, indent=2)

    except Exception as e:
        return f"Tool error: {str(e)}"