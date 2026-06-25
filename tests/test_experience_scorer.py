"""Tests for the experience scorer module."""

import datetime
from src.stage1.experience_scorer import ExperienceScorer

# Test configuration mapping
EXP_SCORES = {
    "optimal": 10.0,
    "mid_low": 5.0,
    "high": 4.0,
    "default": 0.0
}

def test_experience_scorer_direct_field():
    """Tests scoring when direct years_of_experience is provided."""
    scorer = ExperienceScorer(EXP_SCORES)
    
    # 5 years -> Bucket optimal (4-10) -> +10
    cand1 = {"years_of_experience": 5.0}
    score, years = scorer.get_experience_score(cand1)
    assert score == 10.0
    assert years == 5.0

    # 3 years -> Bucket mid_low (2-4) -> +5
    cand2 = {"total_experience_years": 3.0}
    score, years = scorer.get_experience_score(cand2)
    assert score == 5.0
    assert years == 3.0

    # 12 years -> Bucket high (10-15) -> +4
    cand3 = {"experience_years": 12.0}
    score, years = scorer.get_experience_score(cand3)
    assert score == 4.0
    assert years == 12.0

    # 1.5 years -> default -> +0
    cand4 = {"years_of_experience": 1.5}
    score, years = scorer.get_experience_score(cand4)
    assert score == 0.0
    assert years == 1.5

def test_experience_scorer_calculated():
    """Tests experience calculation from dates, including overlapping intervals."""
    scorer = ExperienceScorer(EXP_SCORES)
    
    # 2 non-overlapping jobs: 2 years + 3 years = 5 years
    cand = {
        "experience": [
            {"start_date": "2015-01-01", "end_date": "2017-01-01"},
            {"start_date": "2018-01-01", "end_date": "2021-01-01"}
        ]
    }
    score, years = scorer.get_experience_score(cand)
    assert abs(years - 5.0) < 0.05
    assert score == 10.0

    # 2 overlapping jobs: Job A (2015-2018), Job B (2016-2019)
    # Merged interval should be 2015-2019 (4 years)
    cand_overlap = {
        "work_history": [
            {"start_date": "2015-01-01", "end_date": "2018-01-01"},
            {"start_date": "2016-01-01", "end_date": "2019-01-01"}
        ]
    }
    score, years = scorer.get_experience_score(cand_overlap)
    assert abs(years - 4.0) < 0.05
    assert score == 10.0

    # Job indicating "Present" (uses current date)
    # We will check if it parses successfully without crash.
    cand_present = {
        "experiences": [
            {"start_date": f"{datetime.datetime.today().year - 3}-01-01", "end_date": "Present"}
        ]
    }
    score, years = scorer.get_experience_score(cand_present)
    assert years >= 3.0
