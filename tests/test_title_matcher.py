"""Tests for the title matcher module."""

from src.stage1.title_matcher import TitleMatcher

def test_title_matcher_scoring():
    """Tests that TitleMatcher scores job titles correctly using configurable boosts."""
    title_boosts = {
        "ai engineer": 15.0,
        "software engineer": 5.0,
        "backend engineer": 5.0
    }
    
    matcher = TitleMatcher(title_boosts)
    
    # Simple match
    assert matcher.get_title_score("AI Engineer") == 15.0
    assert matcher.get_title_score("Backend Engineer") == 5.0
    
    # Substring case-insensitive match
    assert matcher.get_title_score("Senior AI Engineer (Remote)") == 15.0
    
    # Multiple matches (matches both "software engineer" and "ai engineer")
    # Should resolve to max boost: 15.0
    assert matcher.get_title_score("AI Engineer, Software Engineer") == 15.0
    
    # No match
    assert matcher.get_title_score("Marketing Specialist") == 0.0
    assert matcher.get_title_score("") == 0.0
    assert matcher.get_title_score(None) == 0.0
