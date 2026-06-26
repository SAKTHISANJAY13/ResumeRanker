"""Feature breakdown and reasoning generator module."""

from typing import Dict, Any

def generate_reasoning(features: Dict[str, Any], score: float) -> str:
    """Generate a human-readable 1-2 sentence reasoning justification for candidate rank.
    
    Args:
        features: Computed candidate feature values.
        score: Final calibrated score.
        
    Returns:
        A concise reasoning string.
    """
    # Extract values safely with robust fallback keys
    exp = float(features.get("experience", features.get("experience_score", features.get("exp", 0.0))))
    skills = float(features.get("skills", features.get("skills_score", 0.0)))
    behavior = float(features.get("behavior", features.get("behavioral_score", 0.0)))
    semantic = float(features.get("semantic", features.get("semantic_score", features.get("semantic_alignment_score", 0.0))))
    penalty = float(features.get("penalty", features.get("anomaly_penalty", features.get("anomaly", 0.0))))

    positives = []
    if exp >= 0.7:
        positives.append(f"strong experience fit ({exp:.2f})")
    elif exp >= 0.4:
        positives.append(f"moderate experience ({exp:.2f})")

    if skills >= 0.7:
        positives.append(f"excellent skill alignment ({skills:.2f})")
    elif skills >= 0.4:
        positives.append(f"decent skill coverage ({skills:.2f})")

    if semantic >= 0.7:
        positives.append(f"high semantic relevance ({semantic:.2f})")
    elif semantic >= 0.4:
        positives.append(f"moderate semantic match ({semantic:.2f})")

    if behavior >= 0.7:
        positives.append(f"strong platform activity ({behavior:.2f})")

    # Sort positives based on scores to present the strongest points first
    # Map back to scores for sorting
    score_map = {
        f"strong experience fit ({exp:.2f})": exp,
        f"moderate experience ({exp:.2f})": exp,
        f"excellent skill alignment ({skills:.2f})": skills,
        f"decent skill coverage ({skills:.2f})": skills,
        f"high semantic relevance ({semantic:.2f})": semantic,
        f"moderate semantic match ({semantic:.2f})": semantic,
        f"strong platform activity ({behavior:.2f})": behavior
    }
    
    positives.sort(key=lambda x: score_map.get(x, 0.0), reverse=True)

    clauses = []
    if positives:
        if len(positives) == 1:
            clauses.append(f"Demonstrates {positives[0]}")
        else:
            clauses.append(f"Demonstrates {positives[0]} and {positives[1]}")
    else:
        clauses.append("Shows moderate overall profile alignment")

    if penalty > 0.0:
        clauses.append(f"with an anomaly penalty of {penalty:.1f} applied for timeline inconsistencies")

    reasoning = ", ".join(clauses).strip()
    if not reasoning.endswith("."):
        reasoning += "."

    return f"{reasoning} Calibrated score: {score:.2f}."

