\"\"\"Common definitions for candidate feature extraction results.\"\"\"

from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass(frozen=True)
class ExperienceFeatures:
    \"\"\"Feature scores/metrics related to candidate's career history.\"\"\"
    years_of_experience: float = 0.0
    num_jobs: int = 0
    average_tenure_months: float = 0.0
    longest_tenure_months: float = 0.0
    career_gap_months: float = 0.0
    seniority_level_score: float = 0.0  # Derived from title progression

@dataclass(frozen=True)
class SkillsFeatures:
    \"\"\"Feature scores/metrics related to candidate's skillset.\"\"\"
    matched_skills_count: int = 0
    expert_skills_count: int = 0
    unmatched_skills_count: int = 0
    endorsements_sum: int = 0
    weighted_skill_proficiency_score: float = 0.0

@dataclass(frozen=True)
class JdAlignmentFeatures:
    \"\"\"Feature scores/metrics measuring similarity with the Job Description.\"\"\"
    headline_similarity: float = 0.0
    summary_similarity: float = 0.0
    title_alignment_score: float = 0.0
    required_keywords_coverage: float = 0.0
    preferred_keywords_coverage: float = 0.0

@dataclass(frozen=True)
class BehavioralFeatures:
    \"\"\"Feature scores/metrics evaluating career behavior/activity.\"\"\"
    job_hopping_index: float = 0.0       # Risk of short stints
    profile_completeness: float = 0.0
    connection_score: float = 0.0
    engagement_frequency_score: float = 0.0

@dataclass(frozen=True)
class LocationFeatures:
    \"\"\"Feature scores/metrics checking geo-proximity and work modes.\"\"\"
    is_exact_location_match: bool = False
    is_country_match: bool = False
    willing_to_relocate: bool = False
    work_mode_compatibility: float = 0.0

@dataclass(frozen=True)
class AnomalyFeatures:
    \"\"\"Feature scores/metrics identifying potential inconsistencies.\"\"\"
    overlapping_dates_detected: bool = False
    invalid_start_end_sequence: bool = False
    high_frequency_job_swaps: bool = False
    missing_critical_data_penalty: float = 0.0

@dataclass(frozen=True)
class CandidateFeatureResult:
    \"\"\"Aggregates all extracted feature sets for a single candidate.\"\"\"
    candidate_id: str
    experience: ExperienceFeatures = field(default_factory=ExperienceFeatures)
    skills: SkillsFeatures = field(default_factory=SkillsFeatures)
    jd_alignment: JdAlignmentFeatures = field(default_factory=JdAlignmentFeatures)
    behavioral: BehavioralFeatures = field(default_factory=BehavioralFeatures)
    location: LocationFeatures = field(default_factory=LocationFeatures)
    anomaly: AnomalyFeatures = field(default_factory=AnomalyFeatures)
