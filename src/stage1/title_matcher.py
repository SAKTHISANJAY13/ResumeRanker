"""Matches candidate current titles against configurable boost criteria."""

from typing import Dict, Optional

class TitleMatcher:
    """Matches and scores candidate current job titles using configurable boosts."""

    def __init__(self, title_boosts: Dict[str, float]):
        """Initializes the TitleMatcher with configured boost weights.
        
        Args:
            title_boosts: A dictionary mapping lowercased title keywords to boost scores.
        """
        # Store lowercased keys for safety
        self.boosts = {title.lower(): weight for title, weight in title_boosts.items()}

    def get_title_score(self, current_title: Optional[str]) -> float:
        """Calculates the boost score for a candidate's current title.
        
        Performs case-insensitive substring matching. If multiple target titles 
        match, the maximum boost score is returned.
        
        Args:
            current_title: The candidate's current job title.
            
        Returns:
            The maximum applicable boost score, or 0.0 if no match.
        """
        if not current_title or not isinstance(current_title, str):
            return 0.0

        title_lower = current_title.lower()
        max_boost = 0.0

        for target_title, boost_val in self.boosts.items():
            if target_title in title_lower:
                if boost_val > max_boost:
                    max_boost = boost_val

        return max_boost
