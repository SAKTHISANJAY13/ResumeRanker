"""Location and work mode compatibility feature engineering module for Stage-2."""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from src.utils.logger import Logger
from stage2.feature_engineering.base import BaseFeatureExtractor

# Try importing the Stage-2 configurations; fall back to defaults if not yet generated
try:
    from stage2.configs.settings import settings
    from stage2.configs.weights import LOCATION_WEIGHTS
    from stage2.configs.keywords import TARGET_CITIES
except ImportError:
    # Production-grade fallback weights and values
    LOCATION_WEIGHTS = {
        "relocation": 0.25,
        "preferred_city": 0.35,
        "hybrid_preference": 0.20,
        "remote_preference": 0.10,
        "notice_period": 0.10
    }
    TARGET_CITIES = [
        "bangalore", "bengaluru", "hyderabad", "pune", 
        "noida", "gurgaon", "chennai", "mumbai"
    ]

# Default constants
MAX_NOTICE_PERIOD_DAYS = 180.0
COMPATIBLE_FLEXIBLE_SCORE = 0.5
FULL_COMPATIBILITY_SCORE = 1.0

@dataclass(frozen=True)
class LocationFeatureResult:
    """Normalized location and availability metrics for a candidate."""
    relocation_score: float
    preferred_city_score: float
    hybrid_preference_score: float
    remote_preference_score: float
    notice_period_score: float
    overall_location_score: float


class LocationFeatureExtractor(BaseFeatureExtractor):
    """Scores geographic compatibility, relocation willingness, and work mode matching."""

    def __init__(self) -> None:
        self.weights = LOCATION_WEIGHTS
        self.target_cities = [city.lower().strip() for city in TARGET_CITIES]

    def _score_preferred_city(self, candidate_location: Optional[str]) -> float:
        """Determines if the candidate is currently in a target preferred city."""
        if not candidate_location or not isinstance(candidate_location, str):
            return 0.0
            
        loc_lower = candidate_location.lower().strip()
        # Substring matching to catch fields like "Bangalore, India" or "Bengaluru Area"
        if any(city in loc_lower for city in self.target_cities):
            return FULL_COMPATIBILITY_SCORE
        return 0.0

    def _score_relocation(self, willing_to_relocate: Any, is_local: bool) -> float:
        """Scores relocation willingness.
        
        If already local, relocation is a non-issue (score = 1.0).
        If not local but willing to relocate, score = 1.0.
        Otherwise, score = 0.0.
        """
        if is_local:
            return FULL_COMPATIBILITY_SCORE
            
        if willing_to_relocate is True or str(willing_to_relocate).lower() == "true":
            return FULL_COMPATIBILITY_SCORE
            
        return 0.0

    def _score_work_modes(self, preferred_mode: Optional[str]) -> tuple[float, float]:
        """Scores hybrid and remote preferences based on candidate work mode choice."""
        if not preferred_mode or not isinstance(preferred_mode, str):
            return 0.0, 0.0
            
        mode_lower = preferred_mode.lower().strip()
        hybrid_score = 0.0
        remote_score = 0.0

        if mode_lower == "hybrid":
            hybrid_score = FULL_COMPATIBILITY_SCORE
        elif mode_lower == "remote":
            remote_score = FULL_COMPATIBILITY_SCORE
        elif mode_lower in ("flexible", "any"):
            hybrid_score = COMPATIBLE_FLEXIBLE_SCORE
            remote_score = COMPATIBLE_FLEXIBLE_SCORE

        return hybrid_score, remote_score

    def _score_notice_period(self, notice_days: Any) -> float:
        """Scores notice period constraint (0 days = 1.0, 180 days = 0.0)."""
        try:
            val = float(notice_days)
            if val <= 0.0:
                return FULL_COMPATIBILITY_SCORE
            if val >= MAX_NOTICE_PERIOD_DAYS:
                return 0.0
            return float(1.0 - (val / MAX_NOTICE_PERIOD_DAYS))
        except (ValueError, TypeError):
            return 0.0

    def extract_features(self, candidate: Dict[str, Any]) -> LocationFeatureResult:
        """Extracts and normalizes location and availability features for a candidate."""
        candidate_id = candidate.get("candidate_id") or candidate.get("id") or "UNKNOWN"
        Logger.info(f"Extracting location features for candidate {candidate_id}")

        profile = candidate.get("profile") or {}
        signals = candidate.get("redrob_signals") or {}

        # 1. Compute individual normalized scores
        pref_city = self._score_preferred_city(profile.get("location"))
        is_local = (pref_city == FULL_COMPATIBILITY_SCORE)
        
        relocation = self._score_relocation(signals.get("willing_to_relocate"), is_local)
        hybrid_pref, remote_pref = self._score_work_modes(signals.get("preferred_work_mode"))
        notice_period = self._score_notice_period(signals.get("notice_period_days"))

        # 2. Compute aggregate location suitability score
        overall_score = (
            relocation * self.weights.get("relocation", 0.0) +
            pref_city * self.weights.get("preferred_city", 0.0) +
            hybrid_pref * self.weights.get("hybrid_preference", 0.0) +
            remote_pref * self.weights.get("remote_preference", 0.0) +
            notice_period * self.weights.get("notice_period", 0.0)
        )

        return LocationFeatureResult(
            relocation_score=relocation,
            preferred_city_score=pref_city,
            hybrid_preference_score=hybrid_pref,
            remote_preference_score=remote_pref,
            notice_period_score=notice_period,
            overall_location_score=float(overall_score)
        )
