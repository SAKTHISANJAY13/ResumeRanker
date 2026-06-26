import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
import functools

class SemanticMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the SemanticMatcher with a SentenceTransformer model.
        Optimized for CPU usage.
        """
        # Force CPU usage for optimization as required
        self.device = torch.device('cpu')
        
        # Set PyTorch threads for CPU optimization
        torch.set_num_threads(4)
        
        self.model = SentenceTransformer(model_name, device=self.device)
        
        # Cache for JD specifically, since it's queried frequently with the same text
        self._jd_cache = {}
        
        # Use lru_cache for candidate texts to prevent memory unbounded growth
        @functools.lru_cache(maxsize=10000)
        def _cached_encode(text: str) -> np.ndarray:
            return self.model.encode(text, convert_to_numpy=True)
            
        self._encode = _cached_encode

    def get_jd_embedding(self, jd_text: str) -> np.ndarray:
        """
        Generates and caches the embedding for the Job Description.
        """
        if jd_text not in self._jd_cache:
            self._jd_cache[jd_text] = self._encode(jd_text)
        return self._jd_cache[jd_text]

    def get_candidate_embedding(self, candidate_text: str) -> np.ndarray:
        """
        Generates and caches the embedding for a candidate text.
        """
        return self._encode(candidate_text)

    def compute_similarity(self, jd_text: str, candidate_text: str) -> float:
        """
        Computes cosine similarity between the Job Description and a candidate text.
        
        Returns:
            semantic_alignment_score (float): The computed alignment score, clipped between -1.0 and 1.0.
        """
        if not jd_text.strip() or not candidate_text.strip():
            return 0.0
            
        jd_emb = self.get_jd_embedding(jd_text).reshape(1, -1)
        cand_emb = self.get_candidate_embedding(candidate_text).reshape(1, -1)
        
        similarity = cosine_similarity(jd_emb, cand_emb)
        semantic_alignment_score = float(similarity[0][0])
        
        # Clip to handle potential float precision issues
        return max(-1.0, min(1.0, semantic_alignment_score))

    def batch_compute_similarity(self, jd_text: str, candidate_texts: List[str]) -> List[float]:
        """
        Computes cosine similarities between the Job Description and multiple candidate texts.
        
        Returns:
            List of semantic_alignment_scores.
        """
        if not jd_text.strip() or not candidate_texts:
            return [0.0] * len(candidate_texts)

        jd_emb = self.get_jd_embedding(jd_text).reshape(1, -1)
        scores = []
        
        for cand_text in candidate_texts:
            if not cand_text.strip():
                scores.append(0.0)
            else:
                cand_emb = self.get_candidate_embedding(cand_text).reshape(1, -1)
                similarity = cosine_similarity(jd_emb, cand_emb)
                semantic_alignment_score = float(similarity[0][0])
                scores.append(max(-1.0, min(1.0, semantic_alignment_score)))
                
        return scores
