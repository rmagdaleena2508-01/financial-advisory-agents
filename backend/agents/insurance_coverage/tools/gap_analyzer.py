from ..schemas.models import GapAnalysisInput, GapAnalysisOutput, RiskLevel


def analyze_coverage_gap(input: GapAnalysisInput) -> GapAnalysisOutput:
    """
    Takes required coverage from DIME and existing coverage.
    Returns gap, risk level, priority action, and handoff trigger.
    """

    total_existing = (
        input.existing_coverage.term_plan_cover
        + input.existing_coverage.employer_group_cover
        + input.existing_coverage.lic_policy_cover
    )

    gap = input.required_coverage - total_existing
    gap = round(gap, 2)

    # Risk classification
    if total_existing == 0:
        risk_level: RiskLevel = "critically_underinsured"
        risk_explanation = (
            "You have zero life insurance coverage. "
            "Your family has no financial protection whatsoever. "
            "This is the highest priority financial risk you face."
        )
        priority_action = (
            "Buy a term life insurance plan immediately. "
            "Even a basic Rs.50L cover is better than nothing. "
            "A healthy person in their 30s can get Rs.1Cr cover for "
            "under Rs.1,000/month premium."
        )

    elif gap > input.required_coverage * 0.5:
        risk_level = "critically_underinsured"
        risk_explanation = (
            f"You are covered for Rs.{total_existing:,.0f} but need "
            f"Rs.{input.required_coverage:,.0f}. "
            f"Your existing coverage covers only "
            f"{(total_existing/input.required_coverage*100):.0f}% of your need. "
            "A significant financial risk exists for your dependents."
        )
        priority_action = (
            f"Increase your term cover by at least Rs.{gap:,.0f}. "
            "Buy a pure term plan — it gives the highest cover at lowest premium. "
            "Do not rely on employer group cover as your primary protection — "
            "it ends when you leave the job."
        )

    elif gap > 0:
        risk_level = "moderately_underinsured"
        risk_explanation = (
            f"You are covered for Rs.{total_existing:,.0f} but need "
            f"Rs.{input.required_coverage:,.0f}. "
            f"Your existing coverage covers "
            f"{(total_existing/input.required_coverage*100):.0f}% of your need. "
            "A moderate gap exists — manageable but should be addressed."
        )
        priority_action = (
            f"Consider topping up your term cover by Rs.{gap:,.0f}. "
            "A top-up plan or a new term policy can close this gap cost-effectively. "
            "Review your coverage at every major life event — "
            "new loan, new child, income increase."
        )

    elif gap == 0:
        risk_level = "adequately_covered"
        risk_explanation = (
            "Your existing coverage exactly matches your calculated need. "
            "You are adequately protected based on current financial profile."
        )
        priority_action = (
            "Review your coverage annually. As income grows or new loans are taken, "
            "your required coverage will increase. "
            "Ensure employer group cover is not counted as your primary protection."
        )

    else:
        risk_level = "over_insured"
        risk_explanation = (
            f"Your existing coverage of Rs.{total_existing:,.0f} exceeds "
            f"your calculated need of Rs.{input.required_coverage:,.0f}. "
            "You may be paying unnecessary premiums."
        )
        priority_action = (
            "Review if all policies are still needed. "
            "As loans are paid off and children become independent, "
            "coverage needs reduce. You could redirect saved premiums to investments."
        )

    # Handoff trigger — only when underinsured
    handoff_triggered = risk_level in [
        "critically_underinsured",
        "moderately_underinsured"
    ]

    handoff_reason = None
    if handoff_triggered:
        handoff_reason = (
            f"User has a coverage gap of Rs.{gap:,.0f}. "
            "This gap should be factored into retirement planning and wealth projection. "
            "HANDOFF:wealth_retirement"
        )

    return GapAnalysisOutput(
        total_existing_coverage=round(total_existing, 2),
        required_coverage=round(input.required_coverage, 2),
        gap=gap,
        risk_level=risk_level,
        risk_explanation=risk_explanation,
        priority_action=priority_action,
        handoff_triggered=handoff_triggered,
        handoff_reason=handoff_reason,
        disclaimer=(
            "Coverage calculations are based on the DIME method and the information "
            "you provided. Actual insurance needs may vary. "
            "This is educational guidance, not regulated insurance advice. "
            "Consult an IRDAI-registered insurance advisor before purchasing any policy."
        )
    )