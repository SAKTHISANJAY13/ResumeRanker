from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseFeatureExtractor(ABC):
    """Abstract base class for all Stage 2 feature extractors."""

    @abstractmethod
    def extract_features(self, candidate: Dict[str, Any]) -> Any:
        """Extracts features from a candidate profile.
        
        Args:
            candidate: Dictionary containing candidate profile data.
            
        Returns:
            A specific FeatureResult dataclass containing computed features.
        """
        pass
