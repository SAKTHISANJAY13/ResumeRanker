\"\"\"Anomaly and risk feature engineering module for Stage-2 reranking.\"\"\"

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Any, Tuple, Optional
from src.utils.logger import Logger

# Try importing the Stage-2 configurations; fall back to defaults if not yet generated
try:
    from stage2.configs.weights import ANOMALY_PENALTIES
    from stage2.configs.settings import settings
except ImportError:
    # Production-grade fallback penalty weights (deducted from candidate rating or added to penalty score)
    ANOMALY_PENALTIES = {
        "invalid_timeline": 5.0,        # Start date after end date
        "overlapping_jobs": 3.0,       # Working multiple concurrent full-time jobs
        "extreme_career_gap": 1.5,     # Gap of > 2 years
        "skill_experience_mismatch": 2.5,# Expert skill claims with minimal actual experience
        "fake_experience_mismatch": 4.0, # Claimed years of experience way exceeds actual career span
        "duplicate_descriptions": 4.5,  # Identical copy-paste career history descriptions
        "unrealistic_promotion": 3.0    # Intern to CTO/Director in under 12 months
    }

# Default thresholds
OVERLAP_THRESHOLD_DAYS = 90
MAX_GAP_THRESHOLD_DAYS = 730
MIN_YEARS_FOR_EXPERT = 1.5
MIN_YEARS_FOR_LEAD = 2.0
CAREER_SPAN_TOLERANCE_YEARS = 2.0
PROM_TIME_THRESHOLD_DAYS = 365

@dataclass(frozen=True)
class AnomalyFeatureResult:
    \"\"\"Dataclass holding anomaly evaluation results for Stage-2 reranking.\"\"\"
    penalty_score: float
    evidence: List[str] = field(default_factory=list)
    confidence: float = 1.0  # Detection confidence (1.0 = highly confident, 0.0 = unsure)


class AnomalyDetector:
    \"\"\"Validates candidate profiles to detect inconsistencies, fake experience, and promotions.\"\"\"

    def __init__(self) -> None:
        self.penalties = ANOMALY_PENALTIES

    def _parse_date(self, date_str: Any) -> Optional[date]:
        \"\"\"Parses candidate career date strings into datetime.date objects.\"\"\"
        if not date_str:
            return None
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, datetime):
            return date_str.date()

        clean_str = str(date_str).strip().lower()
        if clean_str in ("present", "current", "now", "ongoing", "active"):
            return date.today()

        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%Y/%m", "%Y"):
            try:
                return datetime.strptime(clean_str, fmt).date()
            except ValueError:
                continue
        return None

    def extract_features(self, candidate: Dict[str, Any]) -> AnomalyFeatureResult:
        \"\"\"Scans the candidate profile and computes risk metrics.\"\"\"
        candidate_id = candidate.get("candidate_id") or candidate.get("id") or "UNKNOWN"
        Logger.info(f"Running anomaly detection for candidate {candidate_id}")

        penalty_score = 0.0
        evidence: List[str] = []
        checks_run = 0
        checks_succeeded = 0

        # Retrieve career history
        experiences = None
        for key in ("career_history", "experience", "experiences", "work_history"):
            val = candidate.get(key)
            if isinstance(val, list):
                experiences = val
                break

        # If career details are empty, we cannot execute timeline checks safely
        if not experiences:
            return AnomalyFeatureResult(penalty_score=0.0, evidence=[], confidence=0.0)

        # ----------------------------------------------------
        # 1. Detect Impossible Timelines & Concurrent Overlaps
        # ----------------------------------------------------
        checks_run += 1
        intervals: List[Tuple[date, date, str, str]] = []
        has_invalid_date = False

        for idx, exp in enumerate(experiences):
            if not isinstance(exp, dict):
                continue
            
            start_str = exp.get("start_date") or exp.get("from_date")
            end_str = exp.get("end_date") or exp.get("to_date")
            title = exp.get("title") or f"Job {idx+1}"
            company = exp.get("company") or "Unknown Company"

            start_dt = self._parse_date(start_str)
            end_dt = self._parse_date(end_str)
            if not end_dt and (exp.get("is_current") or not end_str):
                end_dt = date.today()

            if start_dt and end_dt:
                if start_dt > end_dt:
                    has_invalid_date = True
                    evidence.append(
                        f"Impossible Timeline: job '{title}' at '{company}' has start date "
                        f"({start_dt}) after end date ({end_dt})."
                    )
                else:
                    intervals.append((start_dt, end_dt, title, company))

        if has_invalid_date:
            penalty_score += self.penalties.get("invalid_timeline", 5.0)
            checks_succeeded += 1

        # Check for overlapping full-time employment intervals
        checks_run += 1
        intervals.sort(key=lambda x: x[0])
        overlapping_found = False
        
        for i in range(len(intervals) - 1):
            s1, e1, t1, c1 = intervals[i]
            s2, e2, t2, c2 = intervals[i+1]
            
            # If the next job starts before the current one ends
            if s2 < e1:
                overlap_days = (e1 - s2).days
                if overlap_days > OVERLAP_THRESHOLD_DAYS:
                    overlapping_found = True
                    evidence.append(
                        f"Overlapping Timeline: Concurrent employment between '{t1}' at '{c1}' "
                        f"and '{t2}' at '{c2}' for {overlap_days} days."
                    )
        
        if overlapping_found:
            penalty_score += self.penalties.get("overlapping_jobs", 3.0)
            checks_succeeded += 1

        # ----------------------------------------------------
        # 2. Career Inconsistencies (Excessive Gaps)
        # ----------------------------------------------------
        checks_run += 1
        large_gap_found = False
        for i in range(len(intervals) - 1):
            _, e1, _, c1 = intervals[i]
            s2, _, _, c2 = intervals[i+1]
            
            if s2 > e1:
                gap_days = (s2 - e1).days
                if gap_days > MAX_GAP_THRESHOLD_DAYS:
                    large_gap_found = True
                    evidence.append(
                        f"Career Inconsistency: Large unexplained gap of {gap_days} days "
                        f"between leaving '{c1}' and joining '{c2}'."
                    )
        if large_gap_found:
            penalty_score += self.penalties.get("extreme_career_gap", 1.5)
            checks_succeeded += 1

        # ----------------------------------------------------
        # 3. Fake Experience (Span mismatches & copies)
        # ----------------------------------------------------
        # Check copy-paste description duplicates
        checks_run += 1
        descriptions: List[str] = []
        duplicate_descriptions = False
        for exp in experiences:
            if isinstance(exp, dict):
                desc = str(exp.get("description") or "").strip()
                if len(desc) > 30:  # Only check substantial texts
                    if desc in descriptions:
                        duplicate_descriptions = True
                    else:
                        descriptions.append(desc)
        if duplicate_descriptions:
            penalty_score += self.penalties.get("duplicate_descriptions", 4.5)
            evidence.append("Fake Experience: Identical job descriptions copy-pasted across multiple roles.")
            checks_succeeded += 1

        # Check total reported years against actual chronological span
        checks_run += 1
        direct_years = 0.0
        for key in ("years_of_experience", "total_experience_years"):
            val = candidate.get("profile", {}).get(key) or candidate.get(key)
            if val is not None:
                try:
                    direct_years = float(val)
                    break
                except (ValueError, TypeError):
                    pass

        if intervals and direct_years > 0.0:
            earliest_start = intervals[0][0]
            latest_end = max(x[1] for x in intervals)
            chronological_span_years = (latest_end - earliest_start).days / 365.25
            
            # If reported years is significantly longer than the actual chronological career window
            if direct_years > (chronological_span_years + CAREER_SPAN_TOLERANCE_YEARS):
                penalty_score += self.penalties.get("fake_experience_mismatch", 4.0)
                evidence.append(
                    f"Fake Experience: Claimed experience of {direct_years} years is unrealistic "
                    f"given a chronological career window of {chronological_span_years:.1f} years."
                )
                checks_succeeded += 1

        # ----------------------------------------------------
        # 4. Skill Inconsistencies
        # ----------------------------------------------------
        checks_run += 1
        skill_mismatch = False
        skills = candidate.get("skills") or []
        for s in skills:
            if isinstance(s, dict):
                name = str(s.get("name") or "").lower()
                proficiency = str(s.get("proficiency") or "").lower()
                
                # If they claim to be an expert in complex ML fields with very low career tenure
                if proficiency in ("expert", "advanced") and direct_years < MIN_YEARS_FOR_EXPERT:
                    if any(term in name for term in ("llm", "deep learning", "machine learning", "neural", "rag")):
                        skill_mismatch = True
                        evidence.append(
                            f"Skill Inconsistency: Candidate claims '{proficiency}' proficiency in "
                            f"'{s.get('name')}' with only {direct_years:.1f} years of total experience."
                        )
                        break

        if skill_mismatch:
            penalty_score += self.penalties.get("skill_experience_mismatch", 2.5)
            checks_succeeded += 1

        # ----------------------------------------------------
        # 5. Unrealistic Promotions
        # ----------------------------------------------------
        checks_run += 1
        unrealistic_promotion = False
        
        # Check rapid promotion within the same company
        # Group jobs by company
        company_jobs: Dict[str, List[Tuple[date, date, str]]] = {}
        for start, end, title, company in intervals:
            co_clean = company.lower().strip()
            if co_clean not in company_jobs:
                company_jobs[co_clean] = []
            company_jobs[co_clean].append((start, end, title.lower()))

        for co, jobs in company_jobs.items():
            if len(jobs) >= 2:
                # Sort jobs by date
                jobs_sorted = sorted(jobs, key=lambda x: x[0])
                for k in range(len(jobs_sorted) - 1):
                    s1, _, t1 = jobs_sorted[k]
                    s2, _, t2 = jobs_sorted[k+1]
                    
                    time_diff_days = (s2 - s1).days
                    
                    # If promoting from intern/junior to director/cto/lead in under a year
                    is_entry = any(x in t1 for x in ("intern", "junior", "trainee", "associate"))
                    is_senior = any(x in t2 for x in ("director", "cto", "vp", "chief", "head", "principal"))
                    
                    if is_entry and is_senior and time_diff_days < PROM_TIME_THRESHOLD_DAYS:
                        unrealistic_promotion = True
                        evidence.append(
                            f"Unrealistic Promotion: Rapid transition from entry role '{t1}' to executive/senior "
                            f"role '{t2}' at '{co}' in {time_diff_days} days."
                        )
                        break

        if unrealistic_promotion:
            penalty_score += self.penalties.get("unrealistic_promotion", 3.0)
            checks_succeeded += 1

        # Confidence is the ratio of successfully parsed checks to run checks
        confidence = float(checks_succeeded / checks_run) if checks_run > 0 else 1.0

        return AnomalyFeatureResult(
            penalty_score=float(penalty_score),
            evidence=evidence,
            confidence=confidence
        )
