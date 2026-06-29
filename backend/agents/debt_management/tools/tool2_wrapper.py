from crewai.tools import tool
from .debt_consolidation_analyzer import run_consolidation_analyzer, ConsolidationInput
from ..schemas.models import Debt, ConsolidationLoan
import json


@tool("Debt Consolidation Analyzer")
def debt_consolidation_analyzer_tool(
    debts_json: str,
    options_json: str,
    user_monthly_income: float
) -> str:
    """
    Analyzes whether consolidating multiple debts into one loan saves money.

    Use this tool when:
    - User asks if they should consolidate their debts
    - User has received a loan offer and wants to know if it is worth it
    - User wants to compare multiple loan options for consolidation
    - User asks about balance transfer offers

    Args:
        debts_json: JSON string of debts to consolidate. Each debt must have:
            name, type, principal_outstanding, interest_rate_pct,
            monthly_emi, tenure_remaining_months

            Example:
            [
              {"name": "HDFC CC", "type": "credit_card", "principal_outstanding": 150000,
               "interest_rate_pct": 36, "monthly_emi": 7500, "tenure_remaining_months": 36}
            ]

        options_json: JSON string of consolidation loan options. Each option must have:
            lender_label, interest_rate_pct, tenure_months, processing_fee_pct

            Example:
            [
              {"lender_label": "Option A", "interest_rate_pct": 13,
               "tenure_months": 36, "processing_fee_pct": 1.0}
            ]

        user_monthly_income (float): User's monthly take-home income in rupees

    Returns:
        JSON with savings analysis per option, best option, and behavioral warning.
    """
    try:
        debts = [Debt(**d) for d in json.loads(debts_json)]
        options = [ConsolidationLoan(**o) for o in json.loads(options_json)]
        result = run_consolidation_analyzer(
            ConsolidationInput(
                debts_to_consolidate=debts,
                consolidation_options=options,
                user_monthly_income=user_monthly_income
            )
        )
        return json.dumps({
            "summary": result.summary,
            "best_option": result.best_option_label,
            "options_analyzed": [
                {
                    "label": r.option_label,
                    "new_emi": r.new_monthly_emi,
                    "net_savings": r.net_savings,
                    "months_to_payoff": r.months_to_payoff,
                    "recommendation": r.recommendation,
                    "behavioral_warning": r.behavioral_warning,
                }
                for r in result.results
            ]
        }, indent=2)

    except json.JSONDecodeError as e:
        return f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return f"Tool error: {str(e)}"