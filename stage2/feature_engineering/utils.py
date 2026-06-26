from typing import Dict, Any, List

def extract_career_history(candidate: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Standardizes the extraction of a candidate's career history block.
    
    Handles various dictionary keys that might represent the work experience array.
    
    Args:
        candidate: The raw candidate dictionary.
        
    Returns:
        A list of experience dictionaries. Returns an empty list if not found.
    """
    for key in ("career_history", "experience", "experiences", "work_history"):
        val = candidate.get(key)
        if isinstance(val, list):
            return val
    return []
