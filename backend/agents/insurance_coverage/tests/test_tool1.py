from ..tools.coverage_need_calculator import calculate_coverage_need
from ..schemas.models import CoverageNeedInput, Liabilities


def make_arjun():
    return CoverageNeedInput(
        monthly_income=120000,
        current_age=34,
        target_retirement_age=60,
        number_of_dependents=1,
        liabilities=Liabilities(
            home_loan_outstanding=3500000,
            personal_loan_outstanding=200000,
            car_loan_outstanding=0,
            credit_card_debt=25000
        ),
        education_goal_per_child=2500000
    )


def make_sneha():
    return CoverageNeedInput(
        monthly_income=75000,
        current_age=29,
        target_retirement_age=58,
        number_of_dependents=1,
        liabilities=Liabilities(
            home_loan_outstanding=0,
            personal_loan_outstanding=150000,
            car_loan_outstanding=400000,
            credit_card_debt=12000
        ),
        education_goal_per_child=0
    )


def make_vikram():
    return CoverageNeedInput(
        monthly_income=300000,
        current_age=45,
        target_retirement_age=55,
        number_of_dependents=2,
        liabilities=Liabilities(
            home_loan_outstanding=8000000,
            personal_loan_outstanding=0,
            car_loan_outstanding=1200000,
            credit_card_debt=0
        ),
        education_goal_per_child=2000000
    )


def test_arjun_dime_components():
    result = calculate_coverage_need(make_arjun())
    assert result.D_debts == 225000
    assert result.M_mortgage == 3500000
    assert result.E_education == 2500000
    assert result.I_income_replacement == 120000 * 12 * 26


def test_sneha_no_mortgage_no_education():
    result = calculate_coverage_need(make_sneha())
    assert result.M_mortgage == 0
    assert result.E_education == 0
    assert result.D_debts == 562000


def test_vikram_years_to_retirement():
    result = calculate_coverage_need(make_vikram())
    assert result.I_income_replacement == 300000 * 12 * 10


def test_vikram_education_multiplied_by_dependents():
    result = calculate_coverage_need(make_vikram())
    assert result.E_education == 2000000 * 2


def test_total_is_sum_of_dime():
    result = calculate_coverage_need(make_arjun())
    expected = (
        result.D_debts
        + result.I_income_replacement
        + result.M_mortgage
        + result.E_education
    )
    assert result.total_required_coverage == round(expected, 2)


def test_already_retired_gives_zero_income_replacement():
    inp = CoverageNeedInput(
        monthly_income=100000,
        current_age=62,
        target_retirement_age=60,
        number_of_dependents=0,
        liabilities=Liabilities(),
        education_goal_per_child=0
    )
    result = calculate_coverage_need(inp)
    assert result.I_income_replacement == 0