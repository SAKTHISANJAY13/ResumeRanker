"""Extracts and scores candidate years of experience."""

from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from src.utils.logger import Logger

class ExperienceScorer:
    """Extracts total years of experience and scores them based on JD guidelines."""

    def __init__(self, experience_scores: Dict[str, float]):
        """Initializes the ExperienceScorer.
        
        Args:
            experience_scores: Dictionary mapping experience buckets to scores.
        """
        self.scores = experience_scores

    def get_experience_score(self, candidate: Dict[str, Any]) -> Tuple[float, float]:
        """Calculates experience score and returns (score, years_of_experience).
        
        Extracts years of experience from direct fields or computes them from 
        experience history using an interval-merging algorithm to avoid double-counting.
        
        Args:
            candidate: Candidate profile dictionary.
            
        Returns:
            Tuple of (experience_score, years_of_experience).
        """
        years = self._extract_years_of_experience(candidate)
        
        # Apply score buckets:
        # 4–10 years  → +10
        # 2–4 years   → +5
        # 10–15 years → +4
        # otherwise   → +0
        if 4.0 <= years <= 10.0:
            score = self.scores.get("optimal", 10.0)
        elif 2.0 <= years < 4.0:
            score = self.scores.get("mid_low", 5.0)
        elif 10.0 < years <= 15.0:
            score = self.scores.get("high", 4.0)
        else:
            score = self.scores.get("default", 0.0)

        return score, years

    def _extract_years_of_experience(self, candidate: Dict[str, Any]) -> float:
        """Helper to extract years of experience from direct fields or career list.
        
        Tries to read direct experience metrics first. If missing, parses and merges
        overlapping start/end dates from the work history list.
        
        Args:
            candidate: Candidate profile dictionary.
            
        Returns:
            Calculated or extracted years of experience as float.
        """
        # 1. Check direct fields first
        for key in ("years_of_experience", "total_experience_years", "experience_years"):
            val = candidate.get(key)
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    pass

        # 2. Compute from experience history
        # Find experience list
        experiences = None
        for exp_key in ("experience", "experiences", "career", "work_history"):
            val = candidate.get(exp_key)
            if isinstance(val, list):
                experiences = val
                break

        if not experiences:
            return 0.0

        intervals: List[Tuple[datetime, datetime]] = []
        today = datetime.today()

        for exp in experiences:
            if not isinstance(exp, dict):
                continue
            
            # Extract start and end dates
            start_str = exp.get("start_date") or exp.get("from_date")
            end_str = exp.get("end_date") or exp.get("to_date")
            
            start_dt = self._parse_date(start_str)
            if not start_dt:
                continue
                
            # If end date is missing or indicates "present", use today's date
            end_dt = self._parse_date(end_str)
            if not end_dt:
                end_dt = today
                
            # Keep start <= end
            if start_dt > end_dt:
                start_dt, end_dt = end_dt, start_dt
                
            intervals.append((start_dt, end_dt))

        if not intervals:
            return 0.0

        # Merge overlapping/adjacent intervals
        intervals.sort(key=lambda x: x[0])
        merged: List[Tuple[datetime, datetime]] = []
        
        for start, end in intervals:
            if not merged:
                merged.append((start, end))
            else:
                last_start, last_end = merged[-1]
                if start <= last_end:
                    # Overlapping or adjacent, merge by updating end date
                    merged[-1] = (last_start, max(last_end, end))
                else:
                    merged.append((start, end))

        # Calculate total days
        total_days = sum((end - start).days for start, end in merged)
        years = total_days / 365.25
        return max(0.0, years)

    @staticmethod
    def _parse_date(date_str: Any) -> Optional[datetime]:
        """Parses a date string in various formats."""
        if not date_str or not isinstance(date_str, str):
            return None
            
        clean_str = date_str.strip().lower()
        if clean_str in ("present", "current", "now", "ongoing", "active"):
            return None
            
        # Try different formats
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%Y/%m", "%Y"):
            try:
                return datetime.strptime(clean_str, fmt)
            except ValueError:
                continue
                
        # Try year extraction if parsing failed (e.g. "June 2018" or "2018")
        # Match a 4-digit number starting with 19 or 20
        import re
        match = re.search(r"\b(19|20)\d{2}\b", clean_str)
        if match:
            try:
                return datetime(year=int(match.group(0)), month=1, day=1)
            except ValueError:
                pass
                
        return None
