"""
Centralized weight configuration for Stage-2 Reranking Pipeline.

This module consolidates all scoring weights, thresholds, and hyperparameters
used across the Stage-2 feature engineering and scoring pipeline.

It provides a single source of truth for tuning the ranking model, enabling
reproducible experiments and easy A/B testing.

Organization:
1. Global Scoring Weights (6 main dimensions → final score)
2. Experience Feature Weights & Thresholds (domain depth & seniority)
3. Skills Feature Weights & Thresholds (technical coverage)
4. JD Alignment Weights & Thresholds (semantic fit with job description)
5. Behavioral Feature Weights & Thresholds (market demand & availability)
6. Location Feature Weights & Thresholds (geographic compatibility)
7. Anomaly Detection Weights & Thresholds (fraud/risk detection)
8. Normalization Constants (score bounds & calibration)

CRITICAL: All weight groups should sum to 1.0. Validation assertions are
included to catch errors during import.

USAGE: Import specific weight dictionaries or constants as needed:
  from stage2.configs.weights import STAGE2_GLOBAL_WEIGHTS
  from stage2.configs.weights import EXPERIENCE_SUB_WEIGHTS
  from stage2.configs.weights import ANOMALY_PENALTIES
"""

# ============================================================================
# 1. GLOBAL SCORING WEIGHTS (Final Score Aggregation)
# ============================================================================
# These weights determine how the 6 main feature dimensions are combined
# into the final candidate score. They sum to 1.0.

STAGE2_GLOBAL_WEIGHTS = {
    "experience": 0.25,           # Years in field, seniority, domain specialization
    "skills": 0.25,               # Technical skill coverage and proficiency
    "alignment": 0.15,            # Job description keyword/concept fit
    "semantic": 0.15,             # Dense vector semantic similarity fit
    "behavior": 0.10,             # Activity signals, engagement, availability
    "location": 0.10,             # Geography, relocation, work mode compatibility
    "penalty_multiplier": 0.05    # Anomaly/fraud deduction factor
}

# Validation: weights should sum to 1.0 (excluding penalty_multiplier which is separate)
assert abs(sum([v for k, v in STAGE2_GLOBAL_WEIGHTS.items() if k != "penalty_multiplier"]) - 1.0) < 1e-6, \
    "Global weights (excluding penalty_multiplier) must sum to 1.0"


# ============================================================================
# 2. EXPERIENCE FEATURE WEIGHTS & THRESHOLDS
# ============================================================================
"""
Measures career depth, seniority progression, and domain specialization.
The experience dimension combines:
- Tenure fitness (overall years, accounting for optimal range)
- Domain-specific expertise (AI, Production ML, Retrieval, Ranking, Recommendations)

CALIBRATION NOTES FOR SENIOR AI ENGINEER - RETRIEVAL & RANKING ROLE:
- Optimal tenure range [4-10 years]: Senior individual contributor, not too green, not too senior
- Domain weights: Retrieval & Ranking 10% each (CRITICAL), AI 20% (foundational), Prod ML 15% (practical)
- Experience caps: Retrieval/Ranking capped at 3.0 years (very rare skill, saturates quickly)
- Current settings: Retrieval experience worth more than general AI knowledge (specialist role)

TUNING NOTES:
- Tenure thresholds (OPTIMAL_EXP_MIN/MAX) should match JD requirements
- Domain caps (AI_EXPERIENCE_CAP, etc.) should be P95 of actual distribution
- If candidates cluster at 10.0 years, OPTIMAL_EXP_MAX is too generous
- If candidates cluster at 3.0 years retrieval, RETRIEVAL_EXPERIENCE_CAP needs validation
"""

# Sub-component weights for experience dimension (sum to 1.0)
EXPERIENCE_SUB_WEIGHTS = {
    "tenure_suitability": 0.40,           # Overall years in field fit to JD range
    "ai_exp": 0.20,                       # Years specifically in AI/ML work
    "prod_ml_exp": 0.15,                  # Years deploying ML systems to production
    "ret_exp": 0.10,                      # Years in retrieval systems (CRITICAL for this JD)
    "rank_exp": 0.10,                     # Years in ranking systems (CRITICAL for this JD)
    "rec_exp": 0.05                       # Years in recommendation systems (bonus)
}

assert abs(sum(EXPERIENCE_SUB_WEIGHTS.values()) - 1.0) < 1e-6, \
    "Experience sub-weights must sum to 1.0"

# Optimal tenure range for a Senior AI Engineer (years)
# Outside this range, score drops (too junior or too senior for active contribution)
OPTIMAL_EXP_MIN = 4.0                     # Minimum experience for "optimal" fit (not too junior)
OPTIMAL_EXP_MAX = 10.0                    # Maximum before diminishing returns (not too senior)
MID_LOW_EXP_MIN = 2.0                     # Lower bound for "acceptable" (but not optimal)
HIGH_EXP_MAX = 15.0                       # Upper bound (beyond this considered less mobile)

# Tenure fit scores at different career lengths
# Maps: [OPTIMAL_MIN, OPTIMAL_MAX] → 1.0 (perfectly suited)
#       [MID_LOW, OPTIMAL_MIN) → 0.5 (junior but capable)
#       (OPTIMAL_MAX, HIGH_MAX] → 0.4 (experienced but possibly overqualified)
#       Otherwise → 0.0 (poor fit, too junior or too senior)
TENURE_FIT_OPTIMAL = 1.0                  # Score for tenure in optimal range [4, 10]
TENURE_FIT_JUNIOR = 0.5                   # Score for under-optimal but capable [2, 4)
TENURE_FIT_SENIOR = 0.4                   # Score for over-optimal but experienced (10, 15]
TENURE_FIT_POOR = 0.0                     # Score for <2 or >15 years (poor fit)

# Domain experience normalization caps (years at which score saturates to 1.0)
# If a candidate has more years than the cap, they get max score (1.0) for that domain.
# These SHOULD be set to P95 (95th percentile) of actual distribution in candidate pool.
# CURRENT SETTINGS: Very conservative (rare skills get low caps)
# TODO: Validate these against actual candidate pool distribution
AI_EXPERIENCE_CAP = 5.0                   # 5 years of AI/ML = excellent (P95 estimate)
PRODUCTION_ML_EXPERIENCE_CAP = 3.0        # 3 years production ML = excellent (rare skill)
RETRIEVAL_EXPERIENCE_CAP = 3.0            # 3 years retrieval = excellent (VERY rare skill)
RANKING_EXPERIENCE_CAP = 3.0              # 3 years ranking = excellent (VERY rare skill)
RECOMMENDATION_EXPERIENCE_CAP = 3.0       # 3 years recommendation = excellent

# Time unit conversion constant
DAYS_PER_YEAR = 365.25                    # Days in a year (used for date calculations)


# ============================================================================
# 3. SKILLS FEATURE WEIGHTS & THRESHOLDS
# ============================================================================
# Measures breadth and depth of technical skill coverage.

# Sub-component weights for skills dimension (sum to 1.0)
SKILLS_SUB_WEIGHTS = {
    "required_coverage": 0.50,             # Ratio of required skills matched
    "preferred_coverage": 0.30,            # Ratio of preferred skills matched
    "bonus_match": 0.20,                   # Count of bonus/nice-to-have skills
    "penalty_deduction": 0.15              # Deduction for red-flag skills (e.g., non-technical roles)
}

assert abs(sum(SKILLS_SUB_WEIGHTS.values()) - 1.0) < 1e-6, \
    "Skills sub-weights must sum to 1.0"

# Normalization caps for skill categories
MAX_BONUS_SKILLS = 3.0                    # More than 3 bonus skills = score capped at 1.0

# NOTE: Specific skill lists (REQUIRED_SKILLS, PREFERRED_SKILLS, etc.) are
#       defined in stage2/configs/keywords.py to keep them separate from weights


# ============================================================================
# 4. JD ALIGNMENT WEIGHTS & THRESHOLDS
# ============================================================================
"""
Measures semantic fit with job description across 8 concept dimensions:
1. Retrieval systems (core skill)
2. Ranking systems (core skill)
3. Vector databases (infrastructure knowledge)
4. Evaluation/metrics (methodological approach)
5. Python (language proficiency)
6. Startup environment (company type match)
7. Product engineering (delivery model)
8. Shipping mindset (culture fit)

MECHANISM: For each dimension, searches candidate profile for keyword matches.
Matches in different text fields are weighted differently (title > skills > description),
and tenure duration multiplies the score (longer jobs = stronger signal).

TUNING NOTES:
- ALIGNMENT_MAX_BOUND should be set to P95 of raw alignment scores across actual candidates
- Current cap (25.0) is ARBITRARY - should be validated against real distribution
- If many candidates score exactly 1.0, the cap is too low
"""

# Sub-component weights for alignment dimension (sum to 1.0)
ALIGNMENT_SUB_WEIGHTS = {
    "retrieval_fit": 0.15,                 # Match on retrieval system concepts
    "ranking_fit": 0.15,                   # Match on ranking system concepts
    "vector_database_fit": 0.15,           # Match on vector database/embedding concepts
    "evaluation_fit": 0.10,                # Match on metrics/evaluation methodologies
    "python_fit": 0.10,                    # Match on Python-specific ecosystem
    "startup_fit": 0.15,                   # Match on startup/scale-up environment signals
    "product_engineering_fit": 0.10,       # Match on product-focused delivery
    "shipping_mindset_fit": 0.10           # Match on shipping/deployment/iteration culture
}

assert abs(sum(ALIGNMENT_SUB_WEIGHTS.values()) - 1.0) < 1e-6, \
    "Alignment sub-weights must sum to 1.0"

# Text field match weights for alignment scoring (_compute_fit method)
# These determine how much each text field contributes to the raw alignment score
# HIGHER = STRONGER SIGNAL
ALIGNMENT_HEADLINE_WEIGHT = 1.5           # Headline/summary match (moderate signal)
ALIGNMENT_SKILL_WEIGHT = 2.0              # Skills list match (strong signal)
ALIGNMENT_TITLE_WEIGHT = 3.0              # Job title match (highest signal)
ALIGNMENT_DESCRIPTION_WEIGHT = 1.0        # Job description match (weak signal)

# Backward compatibility aliases (for modules that import with different names)
SUMMARY_WEIGHT = ALIGNMENT_HEADLINE_WEIGHT
SKILL_WEIGHT = ALIGNMENT_SKILL_WEIGHT
TITLE_WEIGHT = ALIGNMENT_TITLE_WEIGHT
DESCRIPTION_WEIGHT = ALIGNMENT_DESCRIPTION_WEIGHT

# Company size bonus for startup experience
ALIGNMENT_STARTUP_SIZE_BONUS = 2.0        # Extra weight for early-stage companies (1-200 employees)
STARTUP_SIZE_BONUS = ALIGNMENT_STARTUP_SIZE_BONUS

# Default job duration if missing from candidate profile (months)
# Used when career history entry lacks duration_months field
ALIGNMENT_DEFAULT_JOB_DURATION_MONTHS = 6.0  # Assume 6 months if unknown
DEFAULT_JOB_DURATION_MONTHS = ALIGNMENT_DEFAULT_JOB_DURATION_MONTHS

# Normalization cap for alignment raw scores
# Raw alignment scores are UNBOUNDED (accumulate across 8 dimensions and multiple jobs)
# Set this to P95 of actual raw scores to avoid clustering
# CURRENT: 25.0 is ARBITRARY - should be validated with real data
ALIGNMENT_MAX_BOUND = 25.0                # Raw alignment scores capped at this value


# ============================================================================
# 5. BEHAVIORAL FEATURE WEIGHTS & THRESHOLDS
# ============================================================================
"""
Measures engagement signals, market demand, and availability.
The behavioral dimension combines:
- Last active date (recency of profile engagement)
- GitHub activity (open-source contribution signal)
- Response rate to recruiter messages (availability signal)
- Offer acceptance rate (seriousness signal)
- Notice period (time to availability)
- Profile views (market demand signal)
- Saved by recruiters (recruiter interest)
- Search appearance (visibility in searches)

CRITICAL ISSUE: These signals anti-correlate with seniority.
- Senior engineers have LOW profile activity (passive candidates)
- Senior engineers have LONG notice periods (not job-seeking)
- Senior engineers have LOW offer rates (selective)
Using 15% weight for this dimension is APPROPRIATE for passive candidates,
but should be REDUCED (5-8%) if targeting passive senior hires.

TUNING NOTES:
- MAX_* thresholds should be P95 of actual distribution
- Current thresholds are ESTIMATES and should be validated
"""

# Sub-component weights for behavioral dimension (sum to 1.0)
BEHAVIORAL_WEIGHTS = {
    "last_active": 0.20,                  # Recency of last profile activity (strong signal)
    "github": 0.15,                       # GitHub activity score (weak for non-open-source roles)
    "response_rate": 0.15,                # Responsiveness to messages (availability indicator)
    "offer_rate": 0.10,                   # Historical offer acceptance (seriousness indicator)
    "notice_period": 0.15,                # Notice period required (shorter = more available)
    "profile_views": 0.08,                # Profile views in last 30 days (market demand)
    "saved_by_recruiters": 0.12,          # Times saved by recruiters (recruiter interest)
    "search_appearance": 0.05              # Appearance in recruiter searches (visibility)
}

assert abs(sum(BEHAVIORAL_WEIGHTS.values()) - 1.0) < 1e-6, \
    "Behavioral sub-weights must sum to 1.0"

# Last activity recency thresholds (days)
# Scores = 1.0 if active within MIN, → 0.0 if inactive for MAX
BEHAVIORAL_MIN_INACTIVITY_DAYS = 7.0      # Recent = activity within 7 days (score = 1.0)
BEHAVIORAL_MAX_INACTIVITY_DAYS = 180.0    # Stale = no activity for 180+ days (score = 0.0)

# Backward compatibility aliases
MIN_INACTIVITY_DAYS = BEHAVIORAL_MIN_INACTIVITY_DAYS
MAX_INACTIVITY_DAYS = BEHAVIORAL_MAX_INACTIVITY_DAYS

# Notice period thresholds (days)
# Score = 1.0 if available immediately, → 0.0 if notice period >= MAX
BEHAVIORAL_MAX_NOTICE_PERIOD_DAYS = 180.0 # 180 days notice is considered maximum (score = 0.0)

# Backward compatibility alias
MAX_NOTICE_PERIOD_DAYS_BEHAVIORAL = BEHAVIORAL_MAX_NOTICE_PERIOD_DAYS

# Max counts for normalization (use log-scale to handle outliers)
# These should be set to P95 of actual distribution in candidate pool
# If distribution is highly skewed, consider switching to percentile-based normalization
BEHAVIORAL_MAX_PROFILE_VIEWS_30D = 100.0  # More than 100 views/month = score = 1.0
BEHAVIORAL_MAX_SAVED_BY_RECRUITERS_30D = 10.0  # More than 10 saves/month = score = 1.0
BEHAVIORAL_MAX_SEARCH_APPEARANCE_30D = 250.0   # More than 250 appearances/month = score = 1.0

# Backward compatibility aliases
MAX_PROFILE_VIEWS_30D = BEHAVIORAL_MAX_PROFILE_VIEWS_30D
MAX_SAVED_BY_RECRUITERS_30D = BEHAVIORAL_MAX_SAVED_BY_RECRUITERS_30D
MAX_SEARCH_APPEARANCE_30D = BEHAVIORAL_MAX_SEARCH_APPEARANCE_30D


# ============================================================================
# 6. LOCATION FEATURE WEIGHTS & THRESHOLDS
# ============================================================================
# Measures geographic compatibility and work mode preferences.

# Sub-component weights for location dimension (sum to 1.0)
LOCATION_WEIGHTS = {
    "relocation": 0.25,                   # Willingness/ability to relocate
    "preferred_city": 0.35,               # Currently in or close to target location
    "hybrid_preference": 0.20,            # Compatible with hybrid work model
    "remote_preference": 0.10,            # Compatible with remote work model
    "notice_period": 0.10                 # Availability to start (tied to notice period)
}

assert abs(sum(LOCATION_WEIGHTS.values()) - 1.0) < 1e-6, \
    "Location sub-weights must sum to 1.0"

# Location scoring values
LOCATION_FULL_COMPATIBILITY_SCORE = 1.0   # Perfect match (e.g., already in target city)
LOCATION_FLEXIBLE_COMPATIBILITY_SCORE = 0.5  # Partial match (e.g., flexible on work mode)
LOCATION_NO_COMPATIBILITY_SCORE = 0.0     # No match (e.g., unwilling to relocate)

# Notice period thresholds (same as behavioral for consistency)
LOCATION_MAX_NOTICE_PERIOD_DAYS = 180.0   # 180 days notice is considered maximum

# Backward compatibility alias (also used by location.py)
MAX_NOTICE_PERIOD_DAYS = LOCATION_MAX_NOTICE_PERIOD_DAYS


# ============================================================================
# 7. ANOMALY DETECTION WEIGHTS & THRESHOLDS
# ============================================================================
"""
Detects risk flags and fraud indicators:
- Invalid/impossible timelines (data errors)
- Overlapping full-time jobs (unlikely without disclosure)
- Extreme career gaps (red flag for hidden unemployment)
- Skill-experience mismatch (claiming expertise without experience)
- Fake experience (claimed years >> actual career span)
- Duplicate descriptions (copy-paste fraud)
- Unrealistic promotions (entry-level to executive in months)

PENALTY MECHANISM: Each flag adds to a cumulative penalty score.
Higher penalty → larger deduction from final score.

TUNING NOTES:
- Penalty values reflect severity (invalid_timeline=5.0 most severe)
- Thresholds should be calibrated on LABELED validation set
- Use confidence scores to weight uncertainties
"""

# Penalty scores for each type of anomaly detected (cumulative)
# Higher = more severe red flag, larger deduction from final score
ANOMALY_PENALTIES = {
    "invalid_timeline": 5.0,              # Start date after end date (data error or fraud)
    "overlapping_jobs": 3.0,              # Concurrent full-time jobs (unlikely/undisclosed)
    "extreme_career_gap": 1.5,            # Gap > 2 years (hidden unemployment/health issues)
    "skill_experience_mismatch": 2.5,     # Claims "expert" with <1.5 years actual experience
    "fake_experience_mismatch": 4.0,      # Claimed career years >> actual chronological span
    "duplicate_descriptions": 4.5,        # Identical copy-paste in career descriptions (fraud)
    "unrealistic_promotion": 3.0          # Entry-level → executive in <1 year (impossible)
}

# Thresholds for anomaly detection
ANOMALY_OVERLAP_THRESHOLD_DAYS = 90       # Flag overlap if jobs overlap > 90 days
ANOMALY_MAX_GAP_THRESHOLD_DAYS = 730      # Flag gap if > 730 days (2 years)
ANOMALY_MIN_YEARS_FOR_EXPERT = 1.5        # Can't claim "expert" with < 1.5 years
ANOMALY_MIN_YEARS_FOR_LEAD = 2.0          # Minimum years to claim "lead" role
ANOMALY_CAREER_SPAN_TOLERANCE_YEARS = 2.0 # Allow 2-year difference between claimed vs. actual
ANOMALY_PROMOTION_TIME_THRESHOLD_DAYS = 365  # Entry → executive should take > 1 year

# Backward compatibility aliases (for modules that import with different names)
OVERLAP_THRESHOLD_DAYS = ANOMALY_OVERLAP_THRESHOLD_DAYS
MAX_GAP_THRESHOLD_DAYS = ANOMALY_MAX_GAP_THRESHOLD_DAYS
MIN_YEARS_FOR_EXPERT = ANOMALY_MIN_YEARS_FOR_EXPERT
MIN_YEARS_FOR_LEAD = ANOMALY_MIN_YEARS_FOR_LEAD
CAREER_SPAN_TOLERANCE_YEARS = ANOMALY_CAREER_SPAN_TOLERANCE_YEARS
PROM_TIME_THRESHOLD_DAYS = ANOMALY_PROMOTION_TIME_THRESHOLD_DAYS

# Overall thresholds for anomaly impact
ANOMALY_PENALTY_DISQUALIFY_THRESHOLD = 15.0  # If total penalty >= this, candidate disqualified
ANOMALY_CONFIDENCE_MIN_FOR_SCORING = 0.3    # Minimum data quality confidence to trust anomaly score


# ============================================================================
# 8. CALIBRATION & NORMALIZATION CONSTANTS
# ============================================================================
# Used for score normalization and calibration.

# Feature score bounds (all sub-scores should be in [0, 1])
MIN_FEATURE_SCORE = 0.0                   # Minimum possible normalized score
MAX_FEATURE_SCORE = 1.0                   # Maximum possible normalized score

# Final score bounds (after aggregation and penalties)
MIN_FINAL_SCORE = 0.0                     # Candidates can score as low as 0.0
MAX_FINAL_SCORE = 1.0                     # Ideal candidates score close to 1.0

# Percentile-based normalization (if enabled)
# Thresholds for recalibrating scores based on actual candidate distribution
PERCENTILE_FOR_HARD_CAP = 95              # Use P95 of distribution as normalization cap
PERCENTILE_FOR_SOFT_CAP = 90              # Use P90 for softer scaling


# ============================================================================
# SUMMARY OF WEIGHT USAGE
# ============================================================================
"""
Weight Hierarchy & Scoring Formula:

Final Score = weighted_average(
    experience_score * 0.25,
    skills_score * 0.30,
    alignment_score * 0.20,
    behavior_score * 0.15,
    location_score * 0.10
) - (anomaly_penalty * 0.05)

Where each sub-score is calculated as:

experience_score = weighted_average(
    tenure_fit * 0.40,
    ai_score * 0.20,
    prod_ml_score * 0.15,
    retrieval_score * 0.10,
    ranking_score * 0.10,
    recommendation_score * 0.05
)

skills_score = weighted_average(
    required_coverage * 0.50,
    preferred_coverage * 0.30,
    bonus_count_normalized * 0.20
) - (penalty_skill_count * 0.15)

alignment_score = weighted_average(
    retrieval_fit_score * 0.15,
    ranking_fit_score * 0.15,
    vector_db_fit_score * 0.15,
    evaluation_fit_score * 0.10,
    python_fit_score * 0.10,
    startup_fit_score * 0.15,
    product_eng_fit_score * 0.10,
    shipping_fit_score * 0.10
)

behavior_score = weighted_average(
    last_active_normalized * 0.20,
    github_normalized * 0.15,
    response_rate_normalized * 0.15,
    offer_rate_normalized * 0.10,
    notice_period_normalized * 0.15,
    profile_views_normalized * 0.08,
    saved_by_recruiters_normalized * 0.12,
    search_appearance_normalized * 0.05
)

location_score = weighted_average(
    relocation_score * 0.25,
    preferred_city_score * 0.35,
    hybrid_preference_score * 0.20,
    remote_preference_score * 0.10,
    notice_period_score * 0.10
)
"""


# ============================================================================
# VALIDATION & DOCUMENTATION
# ============================================================================

def validate_weights() -> bool:
    """
    Validates that all weight groups sum correctly to 1.0.
    Called automatically on module import.
    
    Returns:
        bool: True if all validations pass
        
    Raises:
        AssertionError: If any weight group doesn't sum to 1.0
    """
    # Global weights validation (excluding penalty_multiplier which is separate)
    global_sum = sum([v for k, v in STAGE2_GLOBAL_WEIGHTS.items() if k != "penalty_multiplier"])
    assert abs(global_sum - 1.0) < 1e-6, \
        f"Global weights must sum to 1.0, got {global_sum}"
    
    # Sub-weight validations
    assert abs(sum(EXPERIENCE_SUB_WEIGHTS.values()) - 1.0) < 1e-6, \
        "Experience sub-weights must sum to 1.0"
    assert abs(sum(SKILLS_SUB_WEIGHTS.values()) - 1.0) < 1e-6, \
        "Skills sub-weights must sum to 1.0"
    assert abs(sum(ALIGNMENT_SUB_WEIGHTS.values()) - 1.0) < 1e-6, \
        "Alignment sub-weights must sum to 1.0"
    assert abs(sum(BEHAVIORAL_WEIGHTS.values()) - 1.0) < 1e-6, \
        "Behavioral sub-weights must sum to 1.0"
    assert abs(sum(LOCATION_WEIGHTS.values()) - 1.0) < 1e-6, \
        "Location sub-weights must sum to 1.0"
    
    return True


# Auto-validate on module import
try:
    validate_weights()
except AssertionError as e:
    raise AssertionError(f"Weight validation failed: {e}")


# ============================================================================
# TUNING GUIDELINES & BEST PRACTICES
# ============================================================================
"""
WEIGHT ADJUSTMENT BEST PRACTICES:


1. UNDERSTAND WEIGHT HIERARCHY:
   final_score = weighted_average(
       experience_score * 0.25,
       skills_score * 0.30,
       alignment_score * 0.20,
       behavior_score * 0.15,
       location_score * 0.10
   ) - (anomaly_penalty * 0.05)

2. DATA-DRIVEN TUNING:
   - Before changing THRESHOLDS, analyze actual candidate distributions
   - If candidates cluster at threshold boundaries → threshold is wrong
   - Use percentile-based caps instead of arbitrary fixed numbers
   - Example: Instead of RETRIEVAL_EXPERIENCE_CAP=3.0, use P95 of real data

3. WEIGHT RATIOS (not absolute values):
   - Changing one weight? Keep others proportional
   - Example: If increasing skills_weight from 0.30 to 0.35, reduce others
   - Maintain sum = 1.0

4. A/B TESTING:
   - Test weight changes on HOLDOUT evaluation set (not training)
   - Measure: Ranking correlation, not absolute scores
   - Track: Margin distribution (how many candidates have close scores)

5. DOMAIN KNOWLEDGE:
   - Weights should reflect JD priorities, not just data distribution
   - Example: For "Retrieval & Ranking" specialist role:
     * retrieval_exp and ranking_exp should have similar weight
     * Even if distribution is skewed toward AI_exp

6. ANOMALY SCORING:
   - Start with HIGH thresholds (few candidates flagged)
   - Gradually LOWER thresholds based on labeled validation
   - Use confidence scores to weight uncertainties
   - Document reason for each threshold change

7. PENALTY HANDLING:
   - Current: Additive (penalty * 0.05 directly subtracted)
   - BETTER: Multiplicative (final_score *= (1 - normalized_penalty))
   - This prevents cliff effects where penalty=20 → score=0

8. DOCUMENTATION:
   - Always document WHY a weight was chosen (not just the value)
   - Include: JD justification, data analysis, A/B test results
   - Link to: experiment numbers, PR discussions, validation reports

COMMON TUNING MISTAKES TO AVOID:

❌ Changing absolute weight without checking sum
❌ Using hard thresholds without validating distribution
❌ Forgetting that penalties apply multiplicatively in impact
❌ Over-weighting signals that anti-correlate with seniority
❌ Tuning on test set (data leakage)
❌ Not measuring ranking correlation (only caring about absolute scores)
❌ Forgetting to update documentation after changes

✅ Always validate with: validate_weights()
✅ Always measure: ranking correlation on holdout set
✅ Always document: why each weight matters
"""
