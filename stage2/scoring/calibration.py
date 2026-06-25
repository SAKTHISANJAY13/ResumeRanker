\"\"\"Reusable score calibration and normalization utility module for Stage-2.\"\"\"

import math
from typing import List, Dict, Union, Optional, Tuple
from src.utils.logger import Logger
from src.common.score import CandidateScore

class ScoreCalibrator:
    \"\"\"Utility class providing standardized normalization and calibration algorithms.\"\"\"

    @staticmethod
    def min_max_scale(
        values: List[float], 
        custom_min: Optional[float] = None, 
        custom_max: Optional[float] = None
    ) -> List[float]:
        \"\"\"Scales values linearly into the standard [0.0, 1.0] range.
        
        Args:
            values: List of raw scores.
            custom_min: Optional global minimum bounds.
            custom_max: Optional global maximum bounds.
            
        Returns:
            MinMax scaled list of float scores.
        \"\"\"
        if not values:
            return []

        val_min = custom_min if custom_min is not None else min(values)
        val_max = custom_max if custom_max is not None else max(values)
        denom = val_max - val_min

        # If all values are identical or bounds are equal, return a neutral score
        if abs(denom) < 1e-9:
            return [1.0 for _ in values]

        return [float((v - val_min) / denom) for v in values]

    @staticmethod
    def z_score_scale(values: List[float]) -> List[float]:
        \"\"\"Standardizes values to have a mean of 0.0 and standard deviation of 1.0.
        
        Args:
            values: List of raw scores.
            
        Returns:
            Z-Score scaled list of float scores.
        \"\"\"
        n = len(values)
        if n == 0:
            return []
        if n == 1:
            return [0.0]

        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = math.sqrt(variance)

        if std_dev < 1e-9:
            return [0.0 for _ in values]

        return [float((x - mean) / std_dev) for x in values]

    @staticmethod
    def percentile_scale(values: List[float], tie_break_strategy: str = "average") -> List[float]:
        \"\"\"Replaces each score with its percentile rank in the dataset.
        
        Args:
            values: List of raw scores.
            tie_break_strategy: Method to handle equal values.
                "average": Assigns the midpoint rank to duplicates.
                "strict": Assigns index rank based on sorting.
                
        Returns:
            Percentile ranks in the range [0.0, 1.0].
        \"\"\"
        n = len(values)
        if n == 0:
            return []
        if n == 1:
            return [1.0]

        if tie_break_strategy == "strict":
            # Sort and assign simple fractional rank based on sorted index
            sorted_indices = sorted(range(n), key=lambda k: values[k])
            ranks = [0.0] * n
            for rank_idx, original_idx in enumerate(sorted_indices):
                ranks[original_idx] = float(rank_idx / (n - 1))
            return ranks

        # Standard statistical mid-percentile formula to handle duplicate values fairly:
        # percentile = (count(y < x) + 0.5 * count(y == x)) / N
        ranks = []
        for x in values:
            count_less = sum(1 for y in values if y < x)
            count_equal = sum(1 for y in values if y == x)
            pct = (count_less + 0.5 * count_equal) / n
            ranks.append(float(pct))
        return ranks

    @classmethod
    def calibrate_scores(
        cls, 
        candidate_scores: List[CandidateScore], 
        method: str = "minmax",
        **kwargs
    ) -> List[CandidateScore]:
        \"\"\"Calibrates list of CandidateScore objects in-place using chosen method.
        
        Args:
            candidate_scores: List of CandidateScore objects.
            method: Normalization type ("minmax", "zscore", "percentile").
            kwargs: Extra parameters passed to the calibration function.
            
        Returns:
            The calibrated CandidateScore list.
        \"\"\"
        if not candidate_scores:
            return []

        raw_scores = [cs.final_score for cs in candidate_scores]
        normalized_scores: List[float] = []

        norm_method = method.strip().lower()
        Logger.info(f"Calibrating {len(candidate_scores)} candidate scores using method '{norm_method}'")

        if norm_method == "minmax":
            custom_min = kwargs.get("custom_min")
            custom_max = kwargs.get("custom_max")
            normalized_scores = cls.min_max_scale(raw_scores, custom_min, custom_max)
        elif norm_method == "zscore":
            normalized_scores = cls.z_score_scale(raw_scores)
        elif norm_method == "percentile":
            tie_break = kwargs.get("tie_break_strategy", "average")
            normalized_scores = cls.percentile_scale(raw_scores, tie_break)
        else:
            Logger.warning(f"Unknown calibration method '{method}'. Leaving scores raw.")
            normalized_scores = raw_scores

        # Update scores in-place
        for score_obj, new_score in zip(candidate_scores, normalized_scores):
            score_obj.final_score = new_score

        return candidate_scores
