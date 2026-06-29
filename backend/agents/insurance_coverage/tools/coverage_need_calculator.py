from ..schemas.models import CoverageNeedInput, DIMEBreakdown


def calculate_coverage_need(input: CoverageNeedInput) -> DIMEBreakdown:
    """
    Runs the DIME method to calculate required life insurance coverage.

    D = Debts (all outstanding loans except home loan + credit card)
    I = Income replacement (annual income x years to retirement)
    M = Mortgage (home loan outstanding)
    E = Education (goal per child x number of dependents who are children)
    """

    # D — Debts (non-mortgage)
    D = (
        input.liabilities.personal_loan_outstanding
        + input.liabilities.car_loan_outstanding
        + input.liabilities.credit_card_debt
    )

    # I — Income replacement
    annual_income = input.monthly_income * 12
    years_to_retirement = max(0, input.target_retirement_age - input.current_age)
    I = annual_income * years_to_retirement

    # M — Mortgage
    M = input.liabilities.home_loan_outstanding

    # E — Education
    E = input.education_goal_per_child * input.number_of_dependents

    total = D + I + M + E

    note = (
        f"D (non-mortgage debts): Rs.{D:,.0f} | "
        f"I (income x {years_to_retirement} years): Rs.{I:,.0f} | "
        f"M (home loan): Rs.{M:,.0f} | "
        f"E (education x {input.number_of_dependents} dependents): Rs.{E:,.0f}"
    )

    return DIMEBreakdown(
        D_debts=round(D, 2),
        I_income_replacement=round(I, 2),
        M_mortgage=round(M, 2),
        E_education=round(E, 2),
        total_required_coverage=round(total, 2),
        calculation_note=note
    )