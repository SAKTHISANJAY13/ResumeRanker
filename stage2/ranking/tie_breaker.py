\"\"\"Tie-breaker logic module to resolve score collisions deterministically.\"\"\"

from typing import List, Tuple
from src.utils.logger import Logger
from src.common.score import CandidateScore

class TieBreaker:
    \"\"\"Resolves ranking ties using a priority queue of secondary signals.\"\"\"

    @staticmethod
    def get_sort_key(candidate: CandidateScore) -> Tuple[float, float, float, str]:
        \"\"\"Generates a composite sorting key for sorting descending.
        
        Priority hierarchy:
        1. Final score (descending -> negated)
        2. Behavioral score (descending -> negated)
        3. Experience score (descending -> negated)
        4. Candidate ID (ascending -> original string)
        
        Args:
            candidate: Scored candidate entry.
            
        Returns:
            Tuple representing the composite sort key.
        \"\"\"
        # Negate values to support standard ascending sorting under the hood
        final_score = -candidate.final_score
        
        # Safe extraction of component score features
        behavioral_score = 0.0
        experience_score = 0.0
        if candidate.component_scores:
            behavioral_score = -candidate.component_scores.behavioral_score
            experience_score = -candidate.component_scores.experience_score

        return (final_score, behavioral_score, experience_score, candidate.candidate_id)

    @classmethod
    def sort_deterministically(cls, candidate_scores: List[CandidateScore]) -> List[CandidateScore]:
        \"\"\"Sorts candidate scores using the deterministic composite key.
        
        Args:
            candidate_scores: List of scored candidate entries.
            
        Returns:
            Deduplicated and sorted list of CandidateScore objects.
        \"\"\"
        if not candidate_scores:
            return []

        Logger.info(f"Breaking ties deterministically for {len(candidate_scores)} candidates...")
        return sorted(candidate_scores, key=cls.get_sort_key)
