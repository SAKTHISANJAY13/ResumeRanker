"""Tests for the filter module."""

from src.stage1.filters import should_reject

UNRELATED_TITLES = ["Marketing Manager", "HR Manager"]

def test_should_reject():
    """Tests the combined Condition A and Condition B rejection logic."""
    
    # Helper functions
    has_rel_true = lambda x: True
    has_rel_false = lambda x: False

    # 1. Condition A is False, Condition B is False (Not unrelated title, has relevance kws)
    # Result: Do NOT reject
    cand1 = {"profile": {"current_title": "AI Engineer"}}
    assert not should_reject(cand1, "python vector", UNRELATED_TITLES, has_rel_true)

    # 2. Condition A is False, Condition B is True (Not unrelated title, NO relevance kws)
    # Result: Do NOT reject (high recall - never reject based only on title)
    cand2 = {"profile": {"current_title": "Software Engineer"}}
    assert not should_reject(cand2, "something else", UNRELATED_TITLES, has_rel_false)

    # 3. Condition A is True, Condition B is False (Unrelated title, but HAS relevance kws)
    # Result: Do NOT reject (retained because of relevance keywords)
    cand3 = {"profile": {"current_title": "Marketing Manager"}}
    assert not should_reject(cand3, "python retrieval", UNRELATED_TITLES, has_rel_true)

    # 4. Condition A is True, Condition B is True (Unrelated title AND NO relevance kws)
    # Result: REJECT (Both conditions met)
    cand4 = {"profile": {"current_title": "HR Manager"}}
    assert should_reject(cand4, "office management supplies", UNRELATED_TITLES, has_rel_false)

    # 5. Missing title (Condition A is False)
    # Result: Do NOT reject
    cand5 = {"profile": {}}
    assert not should_reject(cand5, "no title", UNRELATED_TITLES, has_rel_false)
