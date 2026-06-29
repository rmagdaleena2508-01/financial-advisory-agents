from crewai.tools import tool
from .gap_analyzer import analyze_coverage_gap
from ..schemas.models import GapAnalysisInput, ExistingCoverage
import json


@tool("Coverage Gap Analyzer")
def coverage_gap_analyzer_tool(
    required_coverage: float,
    term_plan_cover: float,
    employer_group_cover: float,
    lic_policy_cover: float
) -> str:
    """
    Analyzes the gap between required life insurance coverage and existing coverage.
    Returns gap amount, risk level, priority action, and handoff signal.

    Use this tool when:
    - User has completed coverage need calculation and shares existing policies
    - User asks if their current insurance is enough
    - User wants to know their insurance gap in rupees
    - User shares their term plan, LIC policy, or employer cover details

    Args:
        required_coverage: Total coverage needed in rupees (from Coverage Need Calculator)
        term_plan_cover: Existing term insurance sum assured in rupees (0 if none)
        employer_group_cover: Employer provided group life cover in rupees (0 if none)
        lic_policy_cover: LIC or other traditional policy sum assured in rupees (0 if none)

    Returns:
        JSON with gap amount, risk classification, action steps, and handoff signal.
    """
    try:
        result = analyze_coverage_gap(GapAnalysisInput(
            required_coverage=required_coverage,
            existing_coverage=ExistingCoverage(
                term_plan_cover=term_plan_cover,
                employer_group_cover=employer_group_cover,
                lic_policy_cover=lic_policy_cover
            )
        ))
        return json.dumps({
            "total_existing_coverage": result.total_existing_coverage,
            "required_coverage": result.required_coverage,
            "gap": result.gap,
            "risk_level": result.risk_level,
            "risk_explanation": result.risk_explanation,
            "priority_action": result.priority_action,
            "handoff_triggered": result.handoff_triggered,
            "handoff_reason": result.handoff_reason,
            "disclaimer": result.disclaimer,
        }, indent=2)

    except Exception as e:
        return f"Tool error: {str(e)}"