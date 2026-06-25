\"\"\"Behavioral feature engineering module for Stage-2 reranking.\"\"\"

import math
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Any, Optional
from src.utils.logger import Logger

# Try importing the Stage-2 configurations; fall back to defaults if not yet generated
try:
    from stage2.configs.settings import settings
    from stage2.configs.weights import BEHAVIORAL_WEIGHTS
except ImportError:
    # Production-grade fallback weights for integrating behavioral scores
    BEHAVIORAL_WEIGHTS = {
        "last_active": 0.20,
        "github": 0.15,
        "response_rate": 0.15,
        "offer_rate": 0.10,
        "notice_period": 0.15,
        "profile_views": 0.08,
        "saved_by_recruiters": 0.12,
        "search_appearance": 0.05
    }

# Max thresholds for normalization scaling to prevent outliers
MAX_NOTICE_PERIOD_DAYS = 180.0
MAX_PROFILE_VIEWS_30D = 100.0
MAX_SAVED_BY_RECRUITERS_30D = 10.0
MAX_SEARCH_APPEARANCE_30D = 250.0

# Inactivity scaling thresholds (days)
MIN_INACTIVITY_DAYS = 7.0
MAX_INACTIVITY_DAYS = 180.0

@dataclass(frozen=True)
class BehavioralFeatureResult:
    \"\"\"Normalized behavioral engagement metrics for a candidate.\"\"\"
    last_active_score: float
    github_score: float
    response_rate_score: float
    offer_rate_score: float
    notice_period_score: float
    profile_views_score: float
    saved_by_recruiters_score: float
    search_appearance_score: float
    overall_behavioral_score: float


class BehavioralFeatureExtractor:
    \"\"\"Extracts and normalizes behavioral metrics into standard [0, 1] signals.\"\"\"

    def __init__(self) -> None:
        self.weights = BEHAVIORAL_WEIGHTS

    def _parse_date(self, date_str: Any) -> Optional[date]:
        \"\"\"Parses candidate activity date strings into datetime.date objects.\"\"\"
        if not date_str:
            return None
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, datetime):
            return date_str.date()

        clean_str = str(date_str).strip().lower()
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%Y/%m", "%Y"):
            try:
                return datetime.strptime(clean_str, fmt).date()
            except ValueError:
                continue
        return None

    def _normalize_last_active(self, last_active_str: Optional[str]) -> float:
        \"\"\"Normalizes last active date into a recency score between 0.0 and 1.0.
        
        Recent activity (<= 7 days) gets 1.0. Inactivity >= 180 days gets 0.0.
        \"\"\"
        last_active_date = self._parse_date(last_active_str)
        if not last_active_date:
            return 0.0
        
        days_inactive = (date.today() - last_active_date).days
        if days_inactive <= MIN_INACTIVITY_DAYS:
            return 1.0
        if days_inactive >= MAX_INACTIVITY_DAYS:
            return 0.0
            
        # Linear interpolation
        range_size = MAX_INACTIVITY_DAYS - MIN_INACTIVITY_DAYS
        return float(1.0 - ((days_inactive - MIN_INACTIVITY_DAYS) / range_size))

    def _normalize_github(self, score: Any) -> float:
        \"\"\"Normalizes Github activity score (0-100) to 0.0-1.0. Maps -1 (no account) to 0.0.\"\"\"
        try:
            val = float(score)
            if val < 0.0:
                return 0.0
            return float(min(val / 100.0, 1.0))
        except (ValueError, TypeError):
            return 0.0

    def _normalize_response_rate(self, rate: Any) -> float:
        \"\"\"Standard response rate is already 0.0 to 1.0.\"\"\"
        try:
            val = float(rate)
            return float(max(0.0, min(val, 1.0)))
        except (ValueError, TypeError):
            return 0.0

    def _normalize_offer_rate(self, rate: Any) -> float:
        \"\"\"Normalizes offer acceptance rate (-1 to 1) to 0.0-1.0 range. Maps -1 to 0.0.\"\"\"
        try:
            val = float(rate)
            if val < 0.0:
                return 0.0
            return float(min(val, 1.0))
        except (ValueError, TypeError):
            return 0.0

    def _normalize_notice_period(self, days: Any) -> float:
        \"\"\"Normalizes notice period. Shorter notice is preferred (0 days = 1.0, 180 days = 0.0).\"\"\"
        try:
            val = float(days)
            if val <= 0.0:
                return 1.0
            if val >= MAX_NOTICE_PERIOD_DAYS:
                return 0.0
            return float(1.0 - (val / MAX_NOTICE_PERIOD_DAYS))
        except (ValueError, TypeError):
            return 0.0

    def _normalize_count(self, count: Any, max_val: float) -> float:
        \"\"\"Log-scaled normalization for counts to reduce the impact of extreme outliers.\"\"\"
        try:
            val = float(count)
            if val <= 0.0:
                return 0.0
            # log(x + 1) normalization
            normalized = math.log1p(val) / math.log1p(max_val)
            return float(min(normalized, 1.0))
        except (ValueError, TypeError):
            return 0.0

    def extract_features(self, candidate: Dict[str, Any]) -> BehavioralFeatureResult:
        \"\"\"Extracts and normalizes behavioral metrics for a candidate profile.\"\"\"
        candidate_id = candidate.get("candidate_id") or candidate.get("id") or "UNKNOWN"
        Logger.info(f"Extracting behavioral features for candidate {candidate_id}")

        signals = candidate.get("redrob_signals") or {}

        # 1. Compute individual normalized scores
        last_active = self._normalize_last_active(signals.get("last_active_date"))
        github = self._normalize_github(signals.get("github_activity_score"))
        response_rate = self._normalize_response_rate(signals.get("recruiter_response_rate"))
        offer_rate = self._normalize_offer_rate(signals.get("offer_acceptance_rate"))
        notice_period = self._normalize_notice_period(signals.get("notice_period_days"))
        
        profile_views = self._normalize_count(
            signals.get("profile_views_received_30d"), MAX_PROFILE_VIEWS_30D
        )
        saved_by_recruiters = self._normalize_count(
            signals.get("saved_by_recruiters_30d"), MAX_SAVED_BY_RECRUITERS_30D
        )
        search_appearance = self._normalize_count(
            signals.get("search_appearance_30d"), MAX_SEARCH_APPEARANCE_30D
        )

        # 2. Compute aggregate behavioral score using config-driven weights
        overall_score = (
            last_active * self.weights.get("last_active", 0.0) +
            github * self.weights.get("github", 0.0) +
            response_rate * self.weights.get("response_rate", 0.0) +
            offer_rate * self.weights.get("offer_rate", 0.0) +
            notice_period * self.weights.get("notice_period", 0.0) +
            profile_views * self.weights.get("profile_views", 0.0) +
            saved_by_recruiters * self.weights.get("saved_by_recruiters", 0.0) +
            search_appearance * self.weights.get("search_appearance", 0.0)
        )

        return BehavioralFeatureResult(
            last_active_score=last_active,
            github_score=github,
            response_rate_score=response_rate,
            offer_rate_score=offer_rate,
            notice_period_score=notice_period,
            profile_views_score=profile_views,
            saved_by_recruiters_score=saved_by_recruiters,
            search_appearance_score=search_appearance,
            overall_behavioral_score=float(overall_score)
        )
