from crewai.tools import tool
from .debt_payoff_optimizer import run_debt_payoff_optimizer, OptimizerInput
from ..schemas.models import Debt
import json


@tool("Debt Payoff Optimizer")
def debt_payoff_optimizer_tool(debts_json: str, extra_monthly_payment: float) -> str:
    """
    Calculates optimal debt repayment strategies using avalanche and snowball methods.

    Use this tool when:
    - User asks how to pay off debts faster
    - User wants to know which debt to pay first
    - User has multiple debts and extra money to allocate
    - User asks about avalanche or snowball method

    Args:
        debts_json: A JSON string representing a list of debts. Each debt must have:
            - name (str): e.g. "HDFC Credit Card"
            - type (str): one of credit_card, personal_loan, home_loan, car_loan, education_loan, bnpl, other
            - principal_outstanding (float): remaining balance in rupees
            - interest_rate_pct (float): annual interest rate e.g. 36.0
            - monthly_emi (float): current monthly payment
            - tenure_remaining_months (int): months left on the debt

            Example:
            [
              {"name": "HDFC CC", "type": "credit_card", "principal_outstanding": 150000,
               "interest_rate_pct": 36, "monthly_emi": 7500, "tenure_remaining_months": 36},
              {"name": "Bajaj PL", "type": "personal_loan", "principal_outstanding": 300000,
               "interest_rate_pct": 14, "monthly_emi": 12000, "tenure_remaining_months": 24}
            ]

        extra_monthly_payment (float): Extra amount user can pay monthly beyond all EMIs

    Returns:
        JSON with both strategies, interest comparison, and recommendation.
    """
    try:
        debts_list = json.loads(debts_json)
        debt_objects = [Debt(**d) for d in debts_list]
        result = run_debt_payoff_optimizer(
            OptimizerInput(
                debts=debt_objects,
                extra_monthly_payment=extra_monthly_payment
            )
        )
        return json.dumps({
            "avalanche": {
                "months_to_debt_free": result.avalanche.months_to_debt_free,
                "total_interest_paid": result.avalanche.total_interest_paid,
                "order_cleared": result.avalanche.order_debts_paid,
            },
            "snowball": {
                "months_to_debt_free": result.snowball.months_to_debt_free,
                "total_interest_paid": result.snowball.total_interest_paid,
                "order_cleared": result.snowball.order_debts_paid,
            },
            "interest_saved_by_avalanche": result.interest_saved_by_avalanche,
            "months_difference": result.months_difference,
            "recommendation": result.recommendation,
            "recommendation_reason": result.recommendation_reason,
        }, indent=2)

    except json.JSONDecodeError as e:
        return f"Invalid JSON format for debts: {str(e)}. Please provide a valid JSON string."
    except Exception as e:
        return f"Tool error: {str(e)}"