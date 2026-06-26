"""Modular scoring framework for the candidate retrieval pipeline."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from src.stage1.title_matcher import TitleMatcher
from src.stage1.keyword_matcher import KeywordMatcher
from src.stage1.experience_scorer import ExperienceScorer

class BaseScorerComponent(ABC):
    """Abstract base class for all scoring pipeline components."""

    @abstractmethod
    def score(self, candidate: Dict[str, Any], searchable_text: str, context: Dict[str, Any]) -> float:
        """Computes a score component for a candidate.
        
        Args:
            candidate: Raw candidate profile dictionary.
            searchable_text: Pre-built lowercased searchable text of candidate.
            context: Shared pipeline context dictionary to store metadata.
            
        Returns:
            The component score as a float.
        """
        pass


class TitleScorerComponent(BaseScorerComponent):
    """Scoring component that boosts candidates based on job titles."""

    def __init__(self, title_matcher: TitleMatcher):
        self.title_matcher = title_matcher

    def score(self, candidate: Dict[str, Any], searchable_text: str, context: Dict[str, Any]) -> float:
        profile = candidate.get("profile") or {}
        current_title = profile.get("current_title")
        score = self.title_matcher.get_title_score(current_title)
        context["title_score"] = score
        return score


class KeywordScorerComponent(BaseScorerComponent):
    """Scoring component that scores candidate text using keywords."""

    def __init__(self, keyword_matcher: KeywordMatcher):
        self.keyword_matcher = keyword_matcher

    def score(self, candidate: Dict[str, Any], searchable_text: str, context: Dict[str, Any]) -> float:
        score = self.keyword_matcher.get_keyword_score(searchable_text)
        context["keyword_score"] = score
        return score


class ExperienceScorerComponent(BaseScorerComponent):
    """Scoring component that scores candidate based on years of experience."""

    def __init__(self, experience_scorer: ExperienceScorer):
        self.experience_scorer = experience_scorer

    def score(self, candidate: Dict[str, Any], searchable_text: str, context: Dict[str, Any]) -> float:
        score, years = self.experience_scorer.get_experience_score(candidate)
        context["experience_score"] = score
        context["years_of_experience"] = years
        return score


class CandidateScorer:
    """Orchestrates candidate scoring by running multiple components."""

    def __init__(self, components: List[BaseScorerComponent]):
        """Initializes CandidateScorer with a list of components.
        
        Args:
            components: List of Scorer Component instances.
        """
        self.components = components

    def score_candidate(self, candidate: Dict[str, Any], searchable_text: str) -> Tuple[float, Dict[str, Any]]:
        """Scores a candidate by executing all registered components.
        
        Args:
            candidate: Raw candidate profile dictionary.
            searchable_text: Pre-built lowercased searchable text of candidate.
            
        Returns:
            Tuple of (total_score, context_dictionary_with_metadata).
        """
        context: Dict[str, Any] = {}
        total_score = 0.0
        
        for component in self.components:
            score = component.score(candidate, searchable_text, context)
            total_score += score
            
        return total_score, context
