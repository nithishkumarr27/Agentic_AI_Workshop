from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Skill(BaseModel):
    name: str
    category: str  # "technical", "soft", "tool", "domain"
    level: SkillLevel
    projects: List[str] = []

class UserProfile(BaseModel):
    name: str
    current_role: str
    skills: List[Skill]
    experience_years: float
    education: List[str]
    projects: List[str]

class RoleRequirement(BaseModel):
    skill: str
    category: str
    importance: str  # "required", "nice_to_have"
    level: SkillLevel

class RoleRequirements(BaseModel):
    role_title: str
    description: str
    requirements: List[RoleRequirement]
    average_salary_range: str
    growth_prospects: str

class GapSeverity(str, Enum):
    CRITICAL = "critical"
    MODERATE = "moderate"
    COVERED = "covered"

class SkillGap(BaseModel):
    skill: str
    current_level: SkillLevel
    required_level: SkillLevel
    gap: GapSeverity
    learning_resources: List[str]

class GapAnalysis(BaseModel):
    role_title: str
    critical_gaps: List[SkillGap]
    moderate_gaps: List[SkillGap]
    covered_skills: List[SkillGap]
    overall_match_percentage: float

class LearningTask(BaseModel):
    title: str
    description: str
    duration_hours: float
    resources: List[str]
    skills_covered: List[str]

class LearningWeek(BaseModel):
    week_number: int
    focus_area: str
    tasks: List[LearningTask]
    milestones: List[str]

class LearningRoadmap(BaseModel):
    role_title: str
    duration_weeks: int
    weeks: List[LearningWeek]
    expected_outcomes: List[str]
    success_metrics: List[str]