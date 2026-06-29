from ..tools.gap_analyzer import analyze_coverage_gap
from ..schemas.models import GapAnalysisInput, ExistingCoverage


def test_zero_coverage_is_critical():
    result = analyze_coverage_gap(GapAnalysisInput(
        required_coverage=10000000,
        existing_coverage=ExistingCoverage(
            term_plan_cover=0,
            employer_group_cover=0,
            lic_policy_cover=0
        )
    ))
    assert result.risk_level == "critically_underinsured"
    assert result.gap == 10000000
    assert result.handoff_triggered is True


def test_large_gap_is_critical():
    result = analyze_coverage_gap(GapAnalysisInput(
        required_coverage=10000000,
        existing_coverage=ExistingCoverage(
            term_plan_cover=2000000,
            employer_group_cover=0,
            lic_policy_cover=0
        )
    ))
    assert result.risk_level == "critically_underinsured"
    assert result.gap == 8000000


def test_moderate_gap():
    result = analyze_coverage_gap(GapAnalysisInput(
        required_coverage=10000000,
        existing_coverage=ExistingCoverage(
            term_plan_cover=7000000,
            employer_group_cover=500000,
            lic_policy_cover=0
        )
    ))
    assert result.risk_level == "moderately_underinsured"
    assert result.gap == 2500000
    assert result.handoff_triggered is True


def test_adequate_coverage():
    result = analyze_coverage_gap(GapAnalysisInput(
        required_coverage=10000000,
        existing_coverage=ExistingCoverage(
            term_plan_cover=10000000,
            employer_group_cover=0,
            lic_policy_cover=0
        )
    ))
    assert result.risk_level == "adequately_covered"
    assert result.gap == 0
    assert result.handoff_triggered is False


def test_over_insured():
    result = analyze_coverage_gap(GapAnalysisInput(
        required_coverage=5000000,
        existing_coverage=ExistingCoverage(
            term_plan_cover=8000000,
            employer_group_cover=1000000,
            lic_policy_cover=0
        )
    ))
    assert result.risk_level == "over_insured"
    assert result.gap < 0
    assert result.handoff_triggered is False


def test_total_existing_is_sum_of_all_covers():
    result = analyze_coverage_gap(GapAnalysisInput(
        required_coverage=10000000,
        existing_coverage=ExistingCoverage(
            term_plan_cover=5000000,
            employer_group_cover=1000000,
            lic_policy_cover=500000
        )
    ))
    assert result.total_existing_coverage == 6500000


def test_disclaimer_always_present():
    result = analyze_coverage_gap(GapAnalysisInput(
        required_coverage=10000000,
        existing_coverage=ExistingCoverage(
            term_plan_cover=5000000,
            employer_group_cover=0,
            lic_policy_cover=0
        )
    ))
    assert len(result.disclaimer) > 0