import re
import json
from typing import Dict, List, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            max_tokens=2048
        )
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Helper method to call LLM with proper error handling"""
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            raise Exception(f"LLM call failed: {str(e)}")
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON response from LLM with error handling"""
        try:
            # Try to extract JSON from response if it's wrapped in markdown
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.rfind("```")
                response = response[json_start:json_end].strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Fallback: try to extract key information using regex
            print(f"JSON parsing failed: {e}. Attempting regex fallback.")
            return self._regex_fallback_parse(response)
    
    def _regex_fallback_parse(self, text: str) -> Dict:
        """Fallback parsing using regex when JSON parsing fails"""
        # This is a basic fallback - can be enhanced based on specific needs
        return {"raw_response": text, "parsed": False}

class ProfileAnalyzerAgent(BaseAgent):
    """Agent for analyzing user profiles and extracting skills"""
    
    def analyze_profile(self, profile_text: str) -> Dict[str, List[str]]:
        """Analyze profile text and extract technical and soft skills"""
        
        system_prompt = """You are an expert HR analyst and career counselor. Your task is to analyze a person's profile/resume and extract their skills accurately.

Guidelines:
1. Extract technical skills (programming languages, tools, frameworks, technologies)
2. Extract soft skills (communication, leadership, problem-solving, etc.)
3. Be specific and accurate - don't hallucinate skills not mentioned
4. Group similar skills appropriately
5. Return the result in valid JSON format

Response format:
{
    "technical_skills": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "experience_years": "X years",
    "domain_expertise": ["domain1", "domain2", ...]
}"""

        prompt = f"""Analyze the following profile/resume text and extract skills:

Profile Text:
{profile_text}

Extract and categorize all mentioned skills. Be accurate and don't add skills that aren't clearly indicated."""

        try:
            response = self._call_llm(prompt, system_prompt)
            parsed_response = self._parse_json_response(response)
            
            # Validate and clean the response
            if not parsed_response.get("parsed", True):
                # Fallback to regex-based extraction
                return self._regex_skill_extraction(profile_text)
            
            return {
                "technical_skills": parsed_response.get("technical_skills", []),
                "soft_skills": parsed_response.get("soft_skills", []),
                "experience_years": parsed_response.get("experience_years", "Not specified"),
                "domain_expertise": parsed_response.get("domain_expertise", [])
            }
            
        except Exception as e:
            print(f"Error in profile analysis: {e}")
            return self._regex_skill_extraction(profile_text)
    
    def _regex_skill_extraction(self, text: str) -> Dict[str, List[str]]:
        """Fallback skill extraction using regex patterns"""
        
        # Common technical skills patterns
        tech_patterns = [
            r'\b(Python|Java|JavaScript|C\+\+|C#|Ruby|PHP|Go|Rust|Swift|Kotlin)\b',
            r'\b(React|Angular|Vue|Django|Flask|Spring|Express|Laravel)\b',
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|Linux)\b',
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch)\b',
            r'\b(HTML|CSS|SQL|NoSQL|REST|GraphQL|API)\b'
        ]
        
        # Common soft skills patterns
        soft_patterns = [
            r'\b(leadership|communication|teamwork|problem.solving)\b',
            r'\b(project.management|agile|scrum|collaboration)\b',
            r'\b(analytical|creative|strategic|innovative)\b'
        ]
        
        technical_skills = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            technical_skills.extend(matches)
        
        soft_skills = []
        for pattern in soft_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            soft_skills.extend([match.replace('.', ' ') for match in matches])
        
        return {
            "technical_skills": list(set(technical_skills)),
            "soft_skills": list(set(soft_skills)),
            "experience_years": "Not specified",
            "domain_expertise": []
        }

class RoleRequirementRetrieverAgent(BaseAgent):
    """Agent for retrieving and analyzing role requirements using RAG"""
    
    def __init__(self, rag_pipeline):
        super().__init__()
        self.rag_pipeline = rag_pipeline
    
    def get_role_requirements(self, role_query: str) -> Dict[str, List[str]]:
        """Retrieve and analyze role requirements using RAG"""
        
        try:
            # Query the vector database for relevant job descriptions
            relevant_docs = self.rag_pipeline.query_documents(role_query, top_k=3)
            
            if not relevant_docs:
                raise Exception("No relevant job descriptions found")
            
            # Combine relevant documents
            combined_context = "\n\n".join([doc['content'] for doc in relevant_docs])
            
            system_prompt = """You are an expert job market analyst. Your task is to analyze job descriptions and extract skill requirements.

Guidelines:
1. Categorize skills into "must_have_skills" (required/essential) and "nice_to_have_skills" (preferred/bonus)
2. Focus on specific, actionable skills
3. Include both technical and soft skills
4. Be comprehensive but realistic
5. Return valid JSON format

Response format:
{
    "must_have_skills": ["skill1", "skill2", ...],
    "nice_to_have_skills": ["skill1", "skill2", ...],
    "role_summary": "Brief role description",
    "seniority_level": "Junior/Mid/Senior"
}"""

            prompt = f"""Analyze the following job description(s) and extract skill requirements:

Job Description(s):
{combined_context}

Extract and categorize all skill requirements. Distinguish between must-have and nice-to-have skills."""

            response = self._call_llm(prompt, system_prompt)
            parsed_response = self._parse_json_response(response)
            
            if not parsed_response.get("parsed", True):
                return self._regex_requirement_extraction(combined_context)
            
            return {
                "must_have_skills": parsed_response.get("must_have_skills", []),
                "nice_to_have_skills": parsed_response.get("nice_to_have_skills", []),
                "role_summary": parsed_response.get("role_summary", ""),
                "seniority_level": parsed_response.get("seniority_level", "Not specified")
            }
            
        except Exception as e:
            print(f"Error in role requirement retrieval: {e}")
            # Fallback to basic skill extraction
            return {
                "must_have_skills": ["Communication", "Problem Solving"],
                "nice_to_have_skills": ["Team Leadership"],
                "role_summary": "Unable to analyze role requirements",
                "seniority_level": "Not specified"
            }
    
    def _regex_requirement_extraction(self, text: str) -> Dict[str, List[str]]:
        """Fallback requirement extraction using regex"""
        
        # Look for requirement keywords
        required_patterns = [
            r'(?:required|must have|essential|mandatory)[:\s]([^.]*)',
            r'(?:minimum|at least)[^:]*:([^.]*)'
        ]
        
        preferred_patterns = [
            r'(?:preferred|nice to have|bonus|plus)[:\s]([^.]*)',
            r'(?:experience with|knowledge of)[:\s]([^.]*)'
        ]
        
        must_have = []
        nice_to_have = []
        
        for pattern in required_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            must_have.extend([match.strip() for match in matches])
        
        for pattern in preferred_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            nice_to_have.extend([match.strip() for match in matches])
        
        return {
            "must_have_skills": must_have[:10],  # Limit to top 10
            "nice_to_have_skills": nice_to_have[:10],
            "role_summary": "Extracted using pattern matching",
            "seniority_level": "Not specified"
        }

class GapAnalysisAgent(BaseAgent):
    """Agent for analyzing skill gaps between profile and role requirements"""
    
    def analyze_gaps(self, user_profile: Dict, role_requirements: Dict) -> Dict[str, List[str]]:
        """Analyze gaps between user profile and role requirements"""
        
        system_prompt = """You are an expert career counselor specializing in skill gap analysis. Your task is to compare a person's current skills with job requirements and identify gaps.

Guidelines:
1. Compare user skills with role requirements
2. Categorize gaps by priority: critical_gaps (must address), intermediate_gaps (should address), bonus_gaps (nice to have)
3. Identify strengths (skills the user already has that match requirements)
4. Be specific and actionable in gap identification
5. Consider both technical and soft skills
6. Return valid JSON format

Response format:
{
    "critical_gaps": ["skill1", "skill2", ...],
    "intermediate_gaps": ["skill1", "skill2", ...],
    "bonus_gaps": ["skill1", "skill2", ...],
    "strengths": ["skill1", "skill2", ...],
    "gap_analysis_summary": "Brief summary of findings"
}"""

        user_skills_text = f"""
Technical Skills: {', '.join(user_profile.get('technical_skills', []))}
Soft Skills: {', '.join(user_profile.get('soft_skills', []))}
Experience: {user_profile.get('experience_years', 'Not specified')}
Domain Expertise: {', '.join(user_profile.get('domain_expertise', []))}
"""

        role_requirements_text = f"""
Must-Have Skills: {', '.join(role_requirements.get('must_have_skills', []))}
Nice-to-Have Skills: {', '.join(role_requirements.get('nice_to_have_skills', []))}
Role Summary: {role_requirements.get('role_summary', '')}
Seniority Level: {role_requirements.get('seniority_level', 'Not specified')}
"""

        prompt = f"""Perform a detailed skill gap analysis:

USER CURRENT SKILLS:
{user_skills_text}

ROLE REQUIREMENTS:
{role_requirements_text}

Analyze the gaps and strengths. Prioritize gaps based on their importance for the role."""

        try:
            response = self._call_llm(prompt, system_prompt)
            parsed_response = self._parse_json_response(response)
            
            if not parsed_response.get("parsed", True):
                return self._basic_gap_analysis(user_profile, role_requirements)
            
            return {
                "critical_gaps": parsed_response.get("critical_gaps", []),
                "intermediate_gaps": parsed_response.get("intermediate_gaps", []),
                "bonus_gaps": parsed_response.get("bonus_gaps", []),
                "strengths": parsed_response.get("strengths", []),
                "gap_analysis_summary": parsed_response.get("gap_analysis_summary", "")
            }
            
        except Exception as e:
            print(f"Error in gap analysis: {e}")
            return self._basic_gap_analysis(user_profile, role_requirements)
    
    def _basic_gap_analysis(self, user_profile: Dict, role_requirements: Dict) -> Dict[str, List[str]]:
        """Basic gap analysis using set operations"""
        
        user_skills = set(user_profile.get('technical_skills', []) + user_profile.get('soft_skills', []))
        must_have = set(role_requirements.get('must_have_skills', []))
        nice_to_have = set(role_requirements.get('nice_to_have_skills', []))
        
        # Simple gap analysis
        critical_gaps = list(must_have - user_skills)
        bonus_gaps = list(nice_to_have - user_skills)
        strengths = list(user_skills.intersection(must_have.union(nice_to_have)))
        
        return {
            "critical_gaps": critical_gaps[:10],
            "intermediate_gaps": [],
            "bonus_gaps": bonus_gaps[:10],
            "strengths": strengths[:10],
            "gap_analysis_summary": "Basic analysis using skill matching"
        }

class RoadmapBuilderAgent(BaseAgent):
    """Agent for building personalized learning roadmaps"""
    
    def build_roadmap(self, gap_analysis: Dict, user_profile: Dict, selected_role: Dict) -> Dict[str, Any]:
        """Build a comprehensive learning roadmap"""
        
        system_prompt = """You are an expert learning and development specialist. Your task is to create personalized, actionable learning roadmaps based on skill gap analysis.

Guidelines:
1. Create milestone-based learning paths
2. Prioritize critical gaps first, then intermediate, then bonus
3. Provide realistic timelines (consider user's current level)
4. Include specific, actionable tasks for each milestone
5. Suggest relevant resources (courses, books, projects)
6. Make the roadmap progressive - each milestone builds on previous ones
7. Return valid JSON format

Response format:
{
    "total_duration": "X weeks/months",
    "milestones": [
        {
            "title": "Milestone Title",
            "duration": "X weeks",
            "description": "What will be achieved",
            "priority": "Critical/Intermediate/Bonus",
            "tasks": ["task1", "task2", ...],
            "resources": ["resource1", "resource2", ...]
        }
    ],
    "daily_commitment": "X hours per day",
    "success_metrics": ["metric1", "metric2", ...]
}"""

        gaps_text = f"""
Critical Gaps: {', '.join(gap_analysis.get('critical_gaps', []))}
Intermediate Gaps: {', '.join(gap_analysis.get('intermediate_gaps', []))}
Bonus Gaps: {', '.join(gap_analysis.get('bonus_gaps', []))}
Current Strengths: {', '.join(gap_analysis.get('strengths', []))}
"""

        context_text = f"""
User Experience: {user_profile.get('experience_years', 'Not specified')}
Target Role: {selected_role.get('requirements', {}).get('role_summary', 'Not specified')}
Seniority Level: {selected_role.get('requirements', {}).get('seniority_level', 'Not specified')}
"""

        prompt = f"""Create a comprehensive learning roadmap:

SKILL GAPS ANALYSIS:
{gaps_text}

CONTEXT:
{context_text}

Create a structured, milestone-based learning plan that addresses the gaps systematically. Focus on practical, achievable goals."""

        try:
            response = self._call_llm(prompt, system_prompt)
            parsed_response = self._parse_json_response(response)
            
            if not parsed_response.get("parsed", True):
                return self._basic_roadmap(gap_analysis)
            
            return {
                "total_duration": parsed_response.get("total_duration", "12-16 weeks"),
                "milestones": parsed_response.get("milestones", []),
                "daily_commitment": parsed_response.get("daily_commitment", "2-3 hours"),
                "success_metrics": parsed_response.get("success_metrics", [])
            }
            
        except Exception as e:
            print(f"Error in roadmap building: {e}")
            return self._basic_roadmap(gap_analysis)
    
    def _basic_roadmap(self, gap_analysis: Dict) -> Dict[str, Any]:
        """Create a basic roadmap when LLM fails"""
        
        milestones = []
        
        # Create milestones based on critical gaps
        critical_gaps = gap_analysis.get('critical_gaps', [])
        if critical_gaps:
            milestones.append({
                "title": "Address Critical Skills",
                "duration": "4-6 weeks",
                "description": "Focus on must-have skills for the role",
                "priority": "Critical",
                "tasks": [f"Learn {skill}" for skill in critical_gaps[:5]],
                "resources": ["Online courses", "Documentation", "Practice projects"]
            })
        
        # Add intermediate gaps
        intermediate_gaps = gap_analysis.get('intermediate_gaps', [])
        if intermediate_gaps:
            milestones.append({
                "title": "Enhance Core Skills",
                "duration": "3-4 weeks",
                "description": "Develop intermediate skills to strengthen your profile",
                "priority": "Intermediate",
                "tasks": [f"Improve {skill}" for skill in intermediate_gaps[:5]],
                "resources": ["Advanced tutorials", "Hands-on projects", "Mentorship"]
            })
        
        # Add bonus skills
        bonus_gaps = gap_analysis.get('bonus_gaps', [])
        if bonus_gaps:
            milestones.append({
                "title": "Bonus Skills Development",
                "duration": "2-3 weeks",
                "description": "Nice-to-have skills that make you stand out",
                "priority": "Bonus",
                "tasks": [f"Explore {skill}" for skill in bonus_gaps[:3]],
                "resources": ["Optional courses", "Side projects", "Community participation"]
            })
        
        return {
            "total_duration": "12-16 weeks",
            "milestones": milestones,
            "daily_commitment": "2-3 hours",
            "success_metrics": [
                "Complete milestone tasks",
                "Build portfolio projects",
                "Practice interview questions",
                "Update resume with new skills"
            ]
        }