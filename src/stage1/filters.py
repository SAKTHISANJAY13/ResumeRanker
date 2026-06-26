"""Implements candidate rejection filters for the retrieval stage."""

from typing import Dict, Any, List, Callable

def should_reject(
    candidate: Dict[str, Any],
    searchable_text: str,
    unrelated_titles: List[str],
    has_relevance_keywords_fn: Callable[[str], bool]
) -> bool:
    """Applies high-recall rejection logic to a candidate.
    
    A candidate is rejected ONLY when BOTH conditions are met:
    - Condition A: Current title is in an unrelated domain (e.g. Marketing Manager).
    - Condition B: No AI/ML/retrieval/ranking keywords appear in their searchable text.
    
    Args:
        candidate: The raw candidate dictionary.
        searchable_text: The candidate's pre-built searchable text representation.
        unrelated_titles: List of lowercase job titles belonging to unrelated domains.
        has_relevance_keywords_fn: Function that checks if text contains relevance keywords.
        
    Returns:
        True if the candidate should be rejected, False otherwise.
    """
    # Extract current title
    profile = candidate.get("profile") or {}
    current_title = profile.get("current_title")
    
    if not current_title or not isinstance(current_title, str):
        # High recall: if current title is missing, do not reject (Condition A is False)
        return False

    current_title_lower = current_title.lower()
    
    # Check Condition A: Current title contains any unrelated title as substring
    is_unrelated_domain = False
    for title in unrelated_titles:
        if title.lower() in current_title_lower:
            is_unrelated_domain = True
            break
            
    if not is_unrelated_domain:
        return False
        
    # Check Condition B: No relevance keywords are matched in the text
    has_relevance = has_relevance_keywords_fn(searchable_text)
    
    # Reject if domain is unrelated AND there are no relevance keywords
    return is_unrelated_domain and not has_relevance
