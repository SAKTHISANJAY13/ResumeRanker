"""Configurable weights for the scoring pipeline components."""

from typing import Dict

# Weights for different keyword groups
KEYWORD_GROUP_WEIGHTS: Dict[str, float] = {
    "GROUP_A": 10.0,
    "GROUP_B": 5.0,
    "GROUP_C": 3.0,
    "GROUP_D": 2.0
}

# Boost weights for candidate current titles (keys are matched case-insensitively)
TITLE_BOOSTS: Dict[str, float] = {
    "ai engineer": 15.0,
    "ml engineer": 15.0,
    "machine learning engineer": 15.0,
    "nlp engineer": 12.0,
    "search engineer": 12.0,
    "ranking engineer": 12.0,
    "recommendation engineer": 12.0,
    "applied scientist": 10.0,
    "data scientist": 8.0,
    "software engineer": 5.0,
    "backend engineer": 5.0,
    "ai research engineer": 12.0
}

# Experience scoring rules
# Mapping years of experience ranges to score values
# 4–10 years  → +10
# 2–4 years   → +5
# 10–15 years → +4
# otherwise   → +0
EXPERIENCE_SCORES: Dict[str, float] = {
    "optimal": 10.0,      # 4 - 10 years
    "mid_low": 5.0,       # 2 - 4 years
    "high": 4.0,          # 10 - 15 years
    "default": 0.0        # otherwise
}
