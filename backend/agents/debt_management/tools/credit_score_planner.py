from pydantic import BaseModel
from typing import Literal
from ..schemas.models import CreditProfile


class ScoreImpactor(BaseModel):
    factor: str
    current_status: str
    impact_level: Literal["critical", "high", "medium", "low"]
    action: str
    estimated_score_gain: str
    timeline_months: int


class CreditScorePlan(BaseModel):
    estimated_current_band: str
    target_band: str
    impactors: list[ScoreImpactor]
    quick_wins: list[str]
    six_month_actions: list[str]
    twelve_month_actions: list[str]
    projected_score_range: str
    disclaimer: str


def _score_band(score: int) -> str:
    if score < 550:  return "Poor (below 550)"
    if score < 650:  return "Fair (550-649)"
    if score < 750:  return "Good (650-749)"
    if score < 800:  return "Very Good (750-799)"
    return "Excellent (800+)"


def _next_band(score: int) -> str:
    if score < 550:  return "Fair (550+)"
    if score < 650:  return "Good (650+)"
    if score < 750:  return "Very Good (750+)"
    if score < 800:  return "Excellent (800+)"
    return "Maintain Excellent (800+)"


def run_credit_score_planner(profile: CreditProfile) -> CreditScorePlan:
    impactors = []
    quick_wins = []
    six_month = []
    twelve_month = []
    projected_gain_low = 0
    projected_gain_high = 0

    # Factor 1: Payment History (35% weight)
    if profile.missed_payments_last_12m >= 3:
        impactors.append(ScoreImpactor(
            factor="Payment history",
            current_status=f"{profile.missed_payments_last_12m} missed payments in 12 months",
            impact_level="critical",
            action=(
                "Set up auto-debit for ALL EMIs and credit card minimum payments "
                "immediately. Even one more missed payment will significantly worsen "
                "your score."
            ),
            estimated_score_gain="30-60 points after 6 months of clean payments",
            timeline_months=6
        ))
        six_month.append(
            "6 consecutive months of zero missed payments — set up auto-debit today"
        )
        projected_gain_low += 30
        projected_gain_high += 60

    elif profile.missed_payments_last_12m in [1, 2]:
        impactors.append(ScoreImpactor(
            factor="Payment history",
            current_status=f"{profile.missed_payments_last_12m} missed payment(s) in 12 months",
            impact_level="high",
            action=(
                "Set up auto-debit to ensure zero missed payments going forward. "
                "The negative impact fades after 12-24 months of clean history."
            ),
            estimated_score_gain="15-30 points after 12 months of clean payments",
            timeline_months=12
        ))
        twelve_month.append(
            "Maintain 12 months of on-time payments — the missed mark fades gradually"
        )
        projected_gain_low += 15
        projected_gain_high += 30

    else:
        impactors.append(ScoreImpactor(
            factor="Payment history",
            current_status="No missed payments — strong",
            impact_level="low",
            action="Maintain this. Confirm auto-debit is active for all accounts.",
            estimated_score_gain="0-5 points (already strong)",
            timeline_months=1
        ))
        quick_wins.append("Confirm auto-debit is active for all accounts")

    # Factor 2: Credit Utilization (30% weight)
    if profile.credit_utilization_pct > 70:
        impactors.append(ScoreImpactor(
            factor="Credit utilization",
            current_status=f"{profile.credit_utilization_pct:.0f}% of total credit limit used",
            impact_level="critical",
            action=(
                f"Pay down credit card balances urgently. Target below 30%. "
                f"This factor updates monthly so improvement shows up fast."
            ),
            estimated_score_gain="40-80 points within 1-2 billing cycles of getting below 30%",
            timeline_months=2
        ))
        quick_wins.append(
            f"Pay down credit cards to get utilization from "
            f"{profile.credit_utilization_pct:.0f}% to below 30%"
        )
        projected_gain_low += 40
        projected_gain_high += 80

    elif profile.credit_utilization_pct > 30:
        impactors.append(ScoreImpactor(
            factor="Credit utilization",
            current_status=f"{profile.credit_utilization_pct:.0f}% of credit limit used",
            impact_level="high",
            action=(
                f"Reduce card usage to bring utilization below 30%. "
                f"Currently at {profile.credit_utilization_pct:.0f}%. "
                "Target below 10% for maximum score impact."
            ),
            estimated_score_gain="15-35 points when below 30%",
            timeline_months=2
        ))
        quick_wins.append(
            "Reduce credit card spend this month to bring utilization below 30%"
        )
        projected_gain_low += 15
        projected_gain_high += 35

    else:
        impactors.append(ScoreImpactor(
            factor="Credit utilization",
            current_status=f"{profile.credit_utilization_pct:.0f}% — healthy",
            impact_level="low",
            action="Keep utilization below 30%. Aim for below 10% for maximum impact.",
            estimated_score_gain="5-10 points if reduced to below 10%",
            timeline_months=1
        ))

    # Factor 3: Credit Age (15% weight)
    years = profile.oldest_account_age_months / 12
    if years < 2:
        impactors.append(ScoreImpactor(
            factor="Credit age",
            current_status=f"Oldest account: {profile.oldest_account_age_months} months",
            impact_level="medium",
            action=(
                "Do NOT close any existing credit accounts, especially older ones. "
                "Age builds passively. Avoid opening multiple new accounts at once."
            ),
            estimated_score_gain="10-20 points over 12-24 months of account aging",
            timeline_months=24
        ))
        twelve_month.append(
            "Keep all existing credit accounts open and active — age builds passively"
        )
        projected_gain_low += 5
        projected_gain_high += 10

    elif years < 5:
        impactors.append(ScoreImpactor(
            factor="Credit age",
            current_status=f"Oldest account: {years:.1f} years — building",
            impact_level="low",
            action="Avoid closing old accounts. Time is the only fix here.",
            estimated_score_gain="5-15 points over the next 2-3 years",
            timeline_months=24
        ))

    else:
        impactors.append(ScoreImpactor(
            factor="Credit age",
            current_status=f"Oldest account: {years:.1f} years — mature",
            impact_level="low",
            action="Strong credit age. Never close your oldest accounts.",
            estimated_score_gain="Already contributing positively",
            timeline_months=0
        ))

    # Factor 4: Hard Inquiries (10% weight)
    if profile.hard_inquiries_last_6m >= 3:
        impactors.append(ScoreImpactor(
            factor="Recent credit inquiries",
            current_status=f"{profile.hard_inquiries_last_6m} hard inquiries in last 6 months",
            impact_level="medium",
            action=(
                "Stop applying for new credit for at least 6 months. "
                "Each hard inquiry lowers score by 5-10 points temporarily. "
                "Multiple inquiries signal credit-seeking behaviour to bureaus."
            ),
            estimated_score_gain="10-20 points after 6 months of no new applications",
            timeline_months=6
        ))
        six_month.append("Pause all new credit applications for 6 months")
        projected_gain_low += 10
        projected_gain_high += 20

    elif profile.hard_inquiries_last_6m >= 1:
        impactors.append(ScoreImpactor(
            factor="Recent credit inquiries",
            current_status=f"{profile.hard_inquiries_last_6m} hard inquiry in last 6 months",
            impact_level="low",
            action="Avoid unnecessary credit applications. Impact fades after 12 months.",
            estimated_score_gain="5-10 points after 12 months",
            timeline_months=12
        ))

    # Sort critical first
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    impactors.sort(key=lambda x: priority_order[x.impact_level])

    current_score = profile.current_score or 600
    projected_low = min(900, current_score + projected_gain_low)
    projected_high = min(900, current_score + projected_gain_high)

    return CreditScorePlan(
        estimated_current_band=(
            _score_band(current_score)
            if profile.current_score
            else "Unknown — provide your score for a better estimate"
        ),
        target_band=_next_band(current_score),
        impactors=impactors,
        quick_wins=quick_wins if quick_wins else ["No urgent quick wins — focus on 6-month actions"],
        six_month_actions=six_month if six_month else ["Maintain current good habits"],
        twelve_month_actions=twelve_month if twelve_month else ["Continue building credit age and clean payment history"],
        projected_score_range=f"{projected_low}-{projected_high} in 12 months (estimate)",
        disclaimer=(
            "Score projections are estimates based on general CIBIL scoring principles. "
            "Actual changes depend on your complete credit profile. "
            "For your official score visit cibil.com. "
            "This is educational guidance, not regulated financial advice."
        )
    )