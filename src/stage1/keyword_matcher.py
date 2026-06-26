"""Matches and scores candidate text against configurable keyword groups."""

import re
from typing import Dict, List, Set, Tuple

class KeywordMatcher:
    """Matches exact keywords and phrases in text with configurable weights."""

    def __init__(self, keyword_groups: Dict[str, List[str]], group_weights: Dict[str, float], relevance_keywords: Set[str]):
        """Initializes the KeywordMatcher.
        
        Args:
            keyword_groups: A dictionary mapping group names (e.g. 'GROUP_A') to lists of keywords/phrases.
            group_weights: A dictionary mapping group names to their float weight values.
            relevance_keywords: A set of keywords used for fast relevance filtering (Condition B).
        """
        self.keyword_patterns: List[Tuple[str, re.Pattern, float]] = []
        
        # Compile individual regexes for keyword scoring
        for group_name, keywords in keyword_groups.items():
            weight = group_weights.get(group_name, 0.0)
            for kw in keywords:
                kw_lower = kw.lower()
                # Compile regex with word boundaries to ensure exact word/phrase matching
                pattern = re.compile(rf"\b{re.escape(kw_lower)}\b")
                self.keyword_patterns.append((kw_lower, pattern, weight))
                
        # Compile a single unified regex for fast relevance checking (Condition B)
        # Sort keywords by length descending to prevent shorter substrings matching inside longer ones
        sorted_rel_kws = sorted(list(relevance_keywords), key=len, reverse=True)
        if sorted_rel_kws:
            pattern_str = r"\b(" + "|".join(re.escape(kw.lower()) for kw in sorted_rel_kws) + r")\b"
            self.relevance_pattern = re.compile(pattern_str)
        else:
            self.relevance_pattern = None

    def get_keyword_score(self, text: str) -> float:
        """Computes the keyword matching score for the given text.
        
        Matches each precompiled keyword/phrase. The score is the sum of 
        the weights of all unique keywords/phrases found in the text.
        
        Args:
            text: Lowercased searchable candidate text.
            
        Returns:
            The total keyword match score.
        """
        score = 0.0
        for _, pattern, weight in self.keyword_patterns:
            if pattern.search(text):
                score += weight
        return score

    def has_relevance_keywords(self, text: str) -> bool:
        """Checks if the text contains any of the AI/ML/retrieval/ranking keywords.
        
        Uses the precompiled unified regex for O(1) matching pass.
        
        Args:
            text: Lowercased searchable candidate text.
            
        Returns:
            True if at least one relevance keyword matches, False otherwise.
        """
        if not self.relevance_pattern:
            return False
        return self.relevance_pattern.search(text) is not None
