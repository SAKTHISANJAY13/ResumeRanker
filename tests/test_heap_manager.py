"""Tests for the heap manager module."""

from src.stage1.heap_manager import HeapManager

def test_heap_manager_basic():
    """Tests basic push and capacity retention of the heap manager."""
    # Heap size K = 3
    manager = HeapManager(k=3)
    
    manager.push(10.0, "cand_A")
    manager.push(5.0, "cand_B")
    manager.push(15.0, "cand_C")
    manager.push(8.0, "cand_D")  # Should pushpop out cand_B (score 5.0)
    
    top_candidates = manager.get_top_k()
    
    # Size should be exactly 3
    assert len(top_candidates) == 3
    
    # Order should be descending by score: C (15), A (10), D (8)
    assert top_candidates[0] == (15.0, "cand_C")
    assert top_candidates[1] == (10.0, "cand_A")
    assert top_candidates[2] == (8.0, "cand_D")

def test_heap_manager_duplicates():
    """Tests that duplicate candidate IDs are not added to the heap."""
    manager = HeapManager(k=5)
    
    manager.push(10.0, "cand_A")
    manager.push(12.0, "cand_A")  # Duplicate ID
    manager.push(5.0, "cand_B")
    
    top_candidates = manager.get_top_k()
    
    # Should only contain cand_A and cand_B once
    assert len(top_candidates) == 2
    assert top_candidates[0] == (10.0, "cand_A")  # Kept the first one
    assert top_candidates[1] == (5.0, "cand_B")
