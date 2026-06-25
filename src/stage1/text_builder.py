"""Constructs searchable text representations from candidate profiles."""

from typing import Dict, Any, List

def build_searchable_text(candidate: Dict[str, Any]) -> str:
    """Builds a lowercase, concatenated text representation of relevant candidate fields.
    
    Includes:
        - profile.headline
        - profile.summary
        - profile.current_title
        - all skill names
        - all career (experience) titles and descriptions
        - all certification names
        
    Args:
        candidate: The raw candidate dictionary.
        
    Returns:
        A lowercase string containing all searchable text content.
    """
    text_parts: List[str] = []
    
    # 1. Profile information
    profile = candidate.get("profile") or {}
    if isinstance(profile, dict):
        for field in ("headline", "summary", "current_title"):
            val = profile.get(field)
            if val and isinstance(val, str):
                text_parts.append(val)

    # 2. Skills
    # Can be candidate.get("skills") -> List of strings or dicts
    skills = candidate.get("skills")
    if isinstance(skills, list):
        for skill in skills:
            if isinstance(skill, str):
                text_parts.append(skill)
            elif isinstance(skill, dict):
                # Try common keys
                for key in ("name", "title", "skill_name", "key"):
                    val = skill.get(key)
                    if val and isinstance(val, str):
                        text_parts.append(val)
                        break

    # 3. Career / Work Experiences
    # Common keys: "experience", "experiences", "career", "work_history"
    experiences = None
    for exp_key in ("experience", "experiences", "career", "work_history"):
        val = candidate.get(exp_key)
        if isinstance(val, list):
            experiences = val
            break
            
    if experiences:
        for exp in experiences:
            if isinstance(exp, dict):
                # Career titles
                for title_key in ("title", "job_title", "role"):
                    t_val = exp.get(title_key)
                    if t_val and isinstance(t_val, str):
                        text_parts.append(t_val)
                        break
                # Career descriptions
                for desc_key in ("description", "job_description", "summary"):
                    d_val = exp.get(desc_key)
                    if d_val and isinstance(d_val, str):
                        text_parts.append(d_val)
                        break

    # 4. Certifications
    # Common keys: "certifications", "certs"
    certs = None
    for cert_key in ("certifications", "certs"):
        val = candidate.get(cert_key)
        if isinstance(val, list):
            certs = val
            break
            
    if certs:
        for cert in certs:
            if isinstance(cert, str):
                text_parts.append(cert)
            elif isinstance(cert, dict):
                for name_key in ("name", "title", "cert_name"):
                    n_val = cert.get(name_key)
                    if n_val and isinstance(n_val, str):
                        text_parts.append(n_val)
                        break

    # Join and normalize to lowercase
    full_text = " ".join(text_parts).lower()
    return full_text
