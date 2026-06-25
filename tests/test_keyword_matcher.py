"""Tests for the keyword matcher module."""

from src.stage1.keyword_matcher import KeywordMatcher

def test_keyword_matcher_exact_and_phrase():
    """Tests keyword matching for exact word matches and multi-word phrases."""
    keyword_groups = {
        "GROUP_A": ["python", "search"],
        "GROUP_B": ["milvus", "hybrid retrieval"]
    }
    group_weights = {
        "GROUP_A": 10.0,
        "GROUP_B": 5.0
    }
    relevance_keywords = {"python", "milvus", "hybrid retrieval"}
    
    matcher = KeywordMatcher(keyword_groups, group_weights, relevance_keywords)
    
    # 1. Test exact word matches
    # "pythonic" should not match "python" due to word boundaries
    text1 = "writing pythonic code using cython."
    assert matcher.get_keyword_score(text1) == 0.0
    assert not matcher.has_relevance_keywords(text1)
    
    # exact "python" should match
    text2 = "expert in python programming."
    assert matcher.get_keyword_score(text2) == 10.0
    assert matcher.has_relevance_keywords(text2)
    
    # 2. Test phrase match
    # phrase "hybrid retrieval" matches
    text3 = "implemented hybrid retrieval for vector databases."
    assert matcher.get_keyword_score(text3) == 5.0
    assert matcher.has_relevance_keywords(text3)
    
    # partial phrase mismatch
    text4 = "this is retrieval but not hybrid."
    assert matcher.get_keyword_score(text4) == 0.0
    
    # 3. Test multiple keyword matches across groups
    text5 = "python engineer using milvus and search."
    # python (10) + search (10) + milvus (5) = 25
    assert matcher.get_keyword_score(text5) == 25.0
    assert matcher.has_relevance_keywords(text5)
