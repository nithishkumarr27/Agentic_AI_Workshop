from typing import Dict, List
from pydantic import BaseModel

class Skill(BaseModel):
    name: str
    category: str  # "technical", "soft", "tool", "domain"
    experience_level: str  # "beginner", "intermediate", "advanced"
    projects: List[str] = []

def extract_skills(text: str) -> Dict:
    """Extract skills from text using LLM (simplified for example)"""
    # In a real implementation, this would use an LLM call
    # For now, return mock data
    return {
        "technical_skills": [
            {"name": "Python", "category": "technical", "experience_level": "intermediate"},
            {"name": "SQL", "category": "technical", "experience_level": "beginner"}
        ],
        "soft_skills": [
            {"name": "Communication", "category": "soft", "experience_level": "advanced"}
        ]
    }