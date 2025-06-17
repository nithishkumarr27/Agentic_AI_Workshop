from typing import List, Dict, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import re
import json
load_dotenv()

class ProfileAnalyzerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", 
                                        google_api_key=os.getenv("GOOGLE_API_KEY"))
        
    def analyze_resume(self, resume_text: str) -> Dict:
        """Analyze resume and extract skills with fallback to regex if LLM fails"""
        # First try with regex (fast but limited)
        regex_skills = self._extract_skills_with_regex(resume_text)
        
        # Then enhance with LLM analysis
        llm_analysis = self._analyze_with_llm(resume_text)
        
        # Combine results with regex as fallback
        return {
            "technical_skills": llm_analysis.get("technical_skills", regex_skills.get("technical", [])),
            "soft_skills": llm_analysis.get("soft_skills", regex_skills.get("soft", [])),
            "experience": llm_analysis.get("experience", {}),
            "education": llm_analysis.get("education", "")
        }
    
    def _extract_skills_with_regex(self, text: str) -> Dict:
        """Extract skills using regex patterns as fallback"""
        technical_patterns = [
            r"\b(?:Python|Java|C\+\+|C#|JavaScript|TypeScript|Go|Rust|Swift|Kotlin)\b",
            r"\b(?:Machine Learning|ML|Deep Learning|DL|Natural Language Processing|NLP|Computer Vision|Data Science)\b",
            r"\b(?:TensorFlow|PyTorch|Keras|scikit-learn|Spark|Hadoop|Pandas|NumPy)\b",
            r"\b(?:SQL|NoSQL|MySQL|PostgreSQL|MongoDB|Redis|Cassandra|Oracle)\b",
            r"\b(?:AWS|Azure|GCP|Docker|Kubernetes|Terraform|Ansible|CI/CD|DevOps)\b",
            r"\b(?:React|Angular|Vue|Node\.js|Django|Flask|Spring|Express)\b"
        ]
        
        soft_patterns = [
            r"\b(?:Leadership|Teamwork|Communication|Problem Solving|Creativity)\b",
            r"\b(?:Time Management|Adaptability|Critical Thinking|Collaboration)\b",
            r"\b(?:Public Speaking|Presentation|Negotiation|Conflict Resolution)\b"
        ]
        
        technical_skills = set()
        for pattern in technical_patterns:
            technical_skills.update(re.findall(pattern, text, re.IGNORECASE))
        
        soft_skills = set()
        for pattern in soft_patterns:
            soft_skills.update(re.findall(pattern, text, re.IGNORECASE))
        
        return {
            "technical": list(technical_skills),
            "soft": list(soft_skills)
        }
    
    def _analyze_with_llm(self, resume_text: str) -> Dict:
        """Use LLM to analyze resume with more structured prompt"""
        prompt = ChatPromptTemplate.from_template("""
        Analyze the following resume text and extract:
        1. Technical skills (programming languages, frameworks, tools) - include proficiency levels if mentioned
        2. Soft skills (communication, leadership, etc.)
        3. Years of experience for each major skill area
        4. Education background (degree, institution, year)
        
        Return ONLY a valid JSON object with these keys:
        {
            "technical_skills": [{"skill": string, "proficiency": string|null}],
            "soft_skills": [string],
            "experience": {"<skill_area>": {"years": number, "details": string}},
            "education": string
        }
        
        If you can't determine something, return null or empty array/object.
        Do NOT include any additional text or explanation.
        
        Resume Text: {resume_text}
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        try:
            result = chain.invoke({"resume_text": resume_text})
            return self._parse_json_output(result)
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return {}
    
    def _parse_json_output(self, text: str) -> Dict:
        """Parse the JSON output from LLM with robust error handling"""
        try:
            # Clean the output in case LLM adds markdown or other formatting
            cleaned = text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:-3].strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:-3].strip()
            
            return json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"Failed to parse LLM output: {text}")
            return {}
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return {}
class RoleRequirementRetrieverAgent:
    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline
    
    def get_requirements(self, role_query: str) -> List[Dict]:
        """Retrieve role requirements using RAG."""
        return self.rag.query_company_requirements(role_query)

class GapAnalysisAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", 
                                        google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    def analyze_gaps(self, profile: Dict, requirements: Dict) -> Dict:
        """Compare profile with requirements and identify gaps."""
        prompt = ChatPromptTemplate.from_template("""
        Compare the candidate's profile with the job requirements and identify skill gaps.
        Categorize each gap as:
        - Critical (must-have skills missing)
        - Intermediate (important but not mandatory skills missing)
        - Bonus (nice-to-have skills missing)
        
        Candidate Profile: {profile}
        
        Job Requirements: {requirements}
        
        Return the analysis in JSON format with keys: critical_gaps, intermediate_gaps, bonus_gaps.
        For each gap, include a brief explanation why it's important.
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "profile": str(profile),
            "requirements": str(requirements)
        })
        return self._parse_json_output(result)
    
    def _parse_json_output(self, text: str) -> Dict:
        try:
            import json
            return json.loads(text)
        except:
            return {
                "critical_gaps": [],
                "intermediate_gaps": [],
                "bonus_gaps": []
            }

class RoadmapBuilderAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", 
                                        google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    def build_roadmap(self, gap_analysis: Dict, timeframe: str = "3 months") -> Dict:
        """Generate learning roadmap based on gaps."""
        prompt = ChatPromptTemplate.from_template("""
        Create a detailed learning roadmap to address the following skill gaps within {timeframe}.
        The roadmap should include:
        - Weekly milestones
        - Recommended resources (free preferred)
        - Estimated time commitment
        - Key outcomes for each milestone
        
        Skill Gaps: {gap_analysis}
        
        Return the roadmap in JSON format with weeks as keys and details as values.
        Include an overall timeline and priority order.
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "gap_analysis": str(gap_analysis),
            "timeframe": timeframe
        })
        return self._parse_json_output(result)
    
    def _parse_json_output(self, text: str) -> Dict:
        try:
            import json
            return json.loads(text)
        except:
            return {"roadmap": "Could not generate roadmap. Please try again."}