"""Manages top-K elements using a min-heap during streaming."""

import heapq
from typing import List, Tuple, Set

class HeapManager:
    """Maintains the top K scored candidates using a min-heap.
    
    Ensures O(N log K) time complexity and O(K) memory usage,
    guaranteeing no duplicate candidate IDs in the final set.
    """

    def __init__(self, k: int):
        """Initializes the HeapManager.
        
        Args:
            k: The number of top candidates to retain (e.g., 20,000).
        """
        self.k = k
        self.heap: List[Tuple[float, str]] = []
        self.heap_ids: Set[str] = set()

    def push(self, score: float, candidate_id: str) -> None:
        """Pushes a candidate score and ID onto the heap.
        
        If the heap size exceeds K, the lowest scoring candidate is popped.
        Ensures uniqueness of candidate IDs.
        
        Args:
            score: The candidate's computed score.
            candidate_id: Unique candidate identifier.
        """
        if not candidate_id:
            return

        # Skip if candidate already exists in the heap to prevent duplicates
        if candidate_id in self.heap_ids:
            return

        if len(self.heap) < self.k:
            heapq.heappush(self.heap, (score, candidate_id))
            self.heap_ids.add(candidate_id)
        elif score > self.heap[0][0]:
            # Push new, pop current minimum
            old_score, old_id = heapq.heappushpop(self.heap, (score, candidate_id))
            self.heap_ids.remove(old_id)
            self.heap_ids.add(candidate_id)

    def get_top_k(self) -> List[Tuple[float, str]]:
        """Returns the top K candidates sorted descending by score.
        
        Returns:
            List of tuples (score, candidate_id) sorted descending.
        """
        # Sort descending by score. For matching scores, sort ascending by candidate_id for deterministic results.
        return sorted(self.heap, key=lambda x: (-x[0], x[1]))

    def __len__(self) -> int:
        """Returns the current size of the heap."""
        return len(self.heap)
