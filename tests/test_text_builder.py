"""Tests for the candidate text builder module."""

from src.stage1.text_builder import build_searchable_text

def test_build_searchable_text_all_fields():
    """Tests text building with a complete candidate profile."""
    candidate = {
        "candidate_id": "1",
        "profile": {
            "headline": "Senior AI Architect",
            "summary": "Building Recommendation Systems",
            "current_title": "AI Tech Lead"
        },
        "skills": [
            "Python",
            {"name": "PyTorch"},
            {"key": "Transformers"}
        ],
        "experience": [
            {
                "title": "Machine Learning Engineer",
                "description": "Designed ranking algorithms."
            }
        ],
        "certifications": [
            "TensorFlow Developer Certificate",
            {"name": "GCP Cloud Architect"}
        ],
        # Excluded fields
        "education": "BS in Computer Science",
        "location": "San Francisco",
        "salary_expectations": "$150,000",
        "preferred_work_mode": "remote"
    }
    
    text = build_searchable_text(candidate)
    
    # Verify everything is lowercased
    assert text == text.lower()
    
    # Verify included fields
    assert "senior ai architect" in text
    assert "recommendation systems" in text
    assert "ai tech lead" in text
    assert "python" in text
    assert "pytorch" in text
    assert "transformers" in text
    assert "machine learning engineer" in text
    assert "designed ranking algorithms" in text
    assert "tensorflow developer certificate" in text
    assert "gcp cloud architect" in text
    
    # Verify excluded fields are NOT in text
    assert "computer science" not in text
    assert "san francisco" not in text
    assert "150,000" not in text
    assert "remote" not in text

def test_build_searchable_text_missing_fields():
    """Tests text building with missing and empty fields."""
    candidate = {
        "candidate_id": "2",
        "profile": None,
        "skills": [],
        "experience": None
    }
    text = build_searchable_text(candidate)
    assert text == ""
