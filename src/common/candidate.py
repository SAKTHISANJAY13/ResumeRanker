"""Common candidate profile models and data structures."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Dict, Optional, Any

class CompanySize(Enum):
    SIZE_1_10 = "1-10"
    SIZE_11_50 = "11-50"
    SIZE_51_200 = "51-200"
    SIZE_201_500 = "201-500"
    SIZE_501_1000 = "501-1000"
    SIZE_1001_5000 = "1001-5000"
    SIZE_5001_10000 = "5001-10000"
    SIZE_10001_PLUS = "10001+"

class InstitutionTier(Enum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    TIER_4 = "tier_4"
    UNKNOWN = "unknown"

class SkillProficiency(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LanguageProficiency(Enum):
    BASIC = "basic"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    NATIVE = "native"

class PreferredWorkMode(Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    FLEXIBLE = "flexible"

@dataclass(frozen=True)
class ExpectedSalaryRange:
    min_lpa: float
    max_lpa: float

@dataclass(frozen=True)
class CandidateProfile:
    anonymized_name: str
    headline: str
    summary: str
    location: str
    country: str
    years_of_experience: float
    current_title: str
    current_company: str
    current_company_size: CompanySize
    current_industry: str

@dataclass(frozen=True)
class CareerHistoryEntry:
    company: str
    title: str
    start_date: str  # Format: YYYY-MM-DD
    end_date: Optional[str]  # Format: YYYY-MM-DD, or None if current
    duration_months: int
    is_current: bool
    industry: str
    company_size: CompanySize
    description: str

@dataclass(frozen=True)
class EducationEntry:
    institution: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int
    grade: Optional[str]
    tier: InstitutionTier

@dataclass(frozen=True)
class SkillEntry:
    name: str
    proficiency: SkillProficiency
    endorsements: int
    duration_months: Optional[int] = None

@dataclass(frozen=True)
class CertificationEntry:
    name: str
    issuer: str
    year: int

@dataclass(frozen=True)
class LanguageEntry:
    language: str
    proficiency: LanguageProficiency

@dataclass(frozen=True)
class RedrobSignals:
    profile_completeness_score: float
    signup_date: str  # Format: YYYY-MM-DD
    last_active_date: str  # Format: YYYY-MM-DD
    open_to_work_flag: bool
    profile_views_received_30d: int
    applications_submitted_30d: int
    recruiter_response_rate: float
    avg_response_time_hours: float
    skill_assessment_scores: Dict[str, float]  # Skill name -> score (0-100)
    connection_count: int
    endorsements_received: int
    notice_period_days: int
    expected_salary_range_inr_lpa: ExpectedSalaryRange
    preferred_work_mode: PreferredWorkMode
    willing_to_relocate: bool
    github_activity_score: float  # -1 if no github linked
    search_appearance_30d: int
    saved_by_recruiters_30d: int
    interview_completion_rate: float
    offer_acceptance_rate: float  # -1 if no offer history
    verified_email: bool
    verified_phone: bool
    linkedin_connected: bool

@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    profile: CandidateProfile
    career_history: List[CareerHistoryEntry] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    skills: List[SkillEntry] = field(default_factory=list)
    redrob_signals: Optional[RedrobSignals] = None
    certifications: List[CertificationEntry] = field(default_factory=list)
    languages: List[LanguageEntry] = field(default_factory=list)
