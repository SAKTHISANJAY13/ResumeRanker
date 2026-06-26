"""Reranking and sorting module for Stage-2 candidate selection."""

from typing import List
from src.utils.logger import Logger
from src.common.score import CandidateScore

class Reranker:
    """Performs stable, deterministic reranking and selects the top K candidates."""

    @staticmethod
    def _get_sort_key(candidate: CandidateScore) -> tuple:
        final_score = -candidate.final_score
        behavioral_score = 0.0
        experience_score = 0.0
        if candidate.component_scores:
            behavioral_score = -candidate.component_scores.behavioral_score
            experience_score = -candidate.component_scores.experience_score
        return (final_score, behavioral_score, experience_score, candidate.candidate_id)

    @staticmethod
    def rerank(
        candidate_scores: List[CandidateScore], 
        top_k: int = 5000
    ) -> List[CandidateScore]:
        """Sorts candidates descending by score and breaks ties deterministically.
        
        Args:
            candidate_scores: List of scored candidate entries.
            top_k: Number of top candidate records to retain.
            
        Returns:
            The sorted and truncated list of CandidateScore objects.
        """
        if not candidate_scores:
            return []

        Logger.info(f"Reranking {len(candidate_scores)} candidates to select Top {top_k}...")

        # Stable and deterministic sort
        sorted_candidates = sorted(candidate_scores, key=Reranker._get_sort_key)

        # Slice to retain top K
        selected_candidates = sorted_candidates[:top_k]

        # Assign ranks in-place to selected candidates (1-based index)
        for idx, candidate in enumerate(selected_candidates, 1):
            candidate.rank = idx

        Logger.info(f"Selected {len(selected_candidates)} candidates successfully.")
        return selected_candidates
