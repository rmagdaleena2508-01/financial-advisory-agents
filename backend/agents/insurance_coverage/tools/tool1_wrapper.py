from crewai.tools import tool
from .coverage_need_calculator import calculate_coverage_need
from .gap_analyzer import analyze_coverage_gap
from ..schemas.models import CoverageNeedInput, Liabilities, GapAnalysisInput, ExistingCoverage
import json


@tool("Insurance Coverage Gap Analyzer")
def insurance_coverage_gap_analyzer_tool(
    monthly_income: float,
    current_age: int,
    target_retirement_age: int,
    number_of_dependents: int,
    home_loan_outstanding: float,
    personal_loan_outstanding: float,
    car_loan_outstanding: float,
    credit_card_debt: float,
    education_goal_per_child: float,
    term_plan_cover: float,
    employer_group_cover: float,
    lic_policy_cover: float
) -> str:
    """
    Calculates life insurance coverage need using DIME method AND
    analyzes the gap against existing coverage in a single step.

    Use this tool when:
    - User asks how much life insurance they need
    - User wants to know their coverage gap
    - User shares income, debts, dependents, and existing policies

    Args:
        monthly_income: Monthly take-home income in rupees
        current_age: Current age in years
        target_retirement_age: Planned retirement age (default 60)
        number_of_dependents: Number of people financially dependent on user
        home_loan_outstanding: Remaining home loan in rupees (0 if none)
        personal_loan_outstanding: Remaining personal loan in rupees (0 if none)
        car_loan_outstanding: Remaining car loan in rupees (0 if none)
        credit_card_debt: Outstanding credit card balance in rupees (0 if none)
        education_goal_per_child: Education corpus target per child in rupees (0 if none)
        term_plan_cover: Existing term insurance sum assured in rupees (0 if none)
        employer_group_cover: Employer group life cover in rupees (0 if none)
        lic_policy_cover: LIC or other traditional policy sum assured in rupees (0 if none)

    Returns:
        JSON with DIME breakdown, required coverage, gap, risk level,
        priority action, and handoff signal.
    """
    try:
        # Step 1 — Calculate coverage need
        need_input = CoverageNeedInput(
            monthly_income=monthly_income,
            current_age=current_age,
            target_retirement_age=target_retirement_age,
            number_of_dependents=number_of_dependents,
            liabilities=Liabilities(
                home_loan_outstanding=home_loan_outstanding,
                personal_loan_outstanding=personal_loan_outstanding,
                car_loan_outstanding=car_loan_outstanding,
                credit_card_debt=credit_card_debt
            ),
            education_goal_per_child=education_goal_per_child
        )
        need_result = calculate_coverage_need(need_input)

        # Step 2 — Analyze gap using exact value from Step 1
        gap_result = analyze_coverage_gap(GapAnalysisInput(
            required_coverage=need_result.total_required_coverage,
            existing_coverage=ExistingCoverage(
                term_plan_cover=term_plan_cover,
                employer_group_cover=employer_group_cover,
                lic_policy_cover=lic_policy_cover
            )
        ))

        return json.dumps({
            "dime_breakdown": {
                "D_debts": need_result.D_debts,
                "I_income_replacement": need_result.I_income_replacement,
                "M_mortgage": need_result.M_mortgage,
                "E_education": need_result.E_education,
                "calculation_note": need_result.calculation_note,
            },
            "required_coverage": need_result.total_required_coverage,
            "existing_coverage": gap_result.total_existing_coverage,
            "gap": gap_result.gap,
            "risk_level": gap_result.risk_level,
            "risk_explanation": gap_result.risk_explanation,
            "priority_action": gap_result.priority_action,
            "handoff_triggered": gap_result.handoff_triggered,
            "handoff_reason": gap_result.handoff_reason,
            "disclaimer": gap_result.disclaimer,
        }, indent=2)

    except Exception as e:
        return f"Tool error: {str(e)}"