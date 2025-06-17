# config.py
import os
from typing import Dict, Any

class Config:
    """Configuration management for the Career Skills Gap Analyzer"""
    
    # API Configuration
    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")
    
    # Model Configuration
    LLM_MODEL = "gemini-1.5-flash"
    EMBEDDING_MODEL = "models/embedding-001"
    LLM_TEMPERATURE = 0.3
    
    # Vector Store Configuration
    VECTOR_STORE_PATH = "faiss_index"
    COMPANY_DATA_PATH = "company_data"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Default Settings
    DEFAULT_TIMEFRAME_WEEKS = 12
    DEFAULT_TOP_K_RESULTS = 3
    DEFAULT_HOURS_PER_WEEK = 15
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.GOOGLE_AI_API_KEY:
            return False
        return True
    
    @classmethod
    def get_sample_job_descriptions(cls) -> Dict[str, str]:
        """Return sample job descriptions for initialization"""
        return {
            "google_ml_engineer": """
            Google - Machine Learning Engineer
            
            Responsibilities:
            - Design and implement machine learning models at scale
            - Work with TensorFlow, PyTorch, and Google Cloud ML
            - Develop MLOps pipelines and model deployment strategies
            - Collaborate with cross-functional teams on AI products
            - Optimize model performance and scalability
            
            Required Skills:
            - 3+ years experience in machine learning
            - Proficiency in Python, TensorFlow, PyTorch
            - Knowledge of statistics, linear algebra, calculus
            - Experience with cloud platforms (GCP preferred)
            - Strong programming and software engineering skills
            - Understanding of distributed systems and scalability
            
            Nice to Have:
            - PhD in Computer Science, Statistics, or related field
            - Experience with large-scale distributed systems
            - Knowledge of MLOps tools (Kubeflow, MLflow)
            - Publications in ML conferences
            - Experience with computer vision or NLP
            """,
            
            "microsoft_data_scientist": """
            Microsoft - Senior Data Scientist
            
            Responsibilities:
            - Build predictive models for business intelligence
            - Analyze large datasets using SQL, Python, R
            - Create data visualizations and reports
            - Present findings to stakeholders and leadership
            - Design A/B tests and experiments
            
            Required Skills:
            - 5+ years experience in data science
            - Expert in Python, R, SQL
            - Knowledge of statistical modeling and hypothesis testing
            - Experience with Azure cloud services
            - Strong communication and presentation skills
            - Experience with data visualization tools (PowerBI, Tableau)
            
            Nice to Have:
            - Master's degree in Data Science, Statistics, or related
            - Experience with deep learning frameworks
            - Knowledge of business domain expertise
            - Certification in Azure Data Science
            - Experience with big data technologies (Spark, Hadoop)
            """,
            
            "amazon_software_engineer": """
            Amazon - Software Development Engineer
            
            Responsibilities:
            - Design and develop scalable web applications
            - Write clean, maintainable code in Java, Python, or JavaScript
            - Participate in code reviews and system design discussions
            - Work in agile development environment
            - Troubleshoot and debug production issues
            
            Required Skills:
            - 2+ years software development experience
            - Proficiency in at least one programming language (Java, Python, C++)
            - Understanding of data structures and algorithms
            - Experience with web development frameworks
            - Knowledge of database systems (SQL, NoSQL)
            - Understanding of software engineering principles
            
            Nice to Have:
            - Bachelor's degree in Computer Science
            - Experience with AWS cloud services
            - Knowledge of microservices architecture
            - Experience with containerization (Docker, Kubernetes)
            - Understanding of DevOps practices
            """,
            
            "netflix_frontend_engineer": """
            Netflix - Senior Frontend Engineer
            
            Responsibilities:
            - Build responsive web applications using React/Vue.js
            - Optimize application performance and user experience
            - Collaborate with designers and backend engineers
            - Implement A/B testing and analytics
            - Ensure cross-browser compatibility
            
            Required Skills:
            - 4+ years frontend development experience
            - Expert in JavaScript, HTML5, CSS3
            - Proficiency in React, Vue.js, or Angular
            - Experience with state management (Redux, Vuex)
            - Knowledge of build tools (Webpack, Vite)
            - Understanding of responsive design principles
            
            Nice to Have:
            - Experience with TypeScript
            - Knowledge of testing frameworks (Jest, Cypress)
            - Understanding of web performance optimization
            - Experience with GraphQL
            - Knowledge of accessibility standards (WCAG)
            """,
            
            "openai_research_scientist": """
            OpenAI - Research Scientist
            
            Responsibilities:
            - Conduct cutting-edge research in artificial intelligence
            - Develop novel algorithms and models
            - Publish research papers in top-tier conferences
            - Collaborate with engineering teams on implementation
            - Mentor junior researchers and interns
            
            Required Skills:
            - PhD in Computer Science, Mathematics, or related field
            - 3+ years research experience in AI/ML
            - Strong mathematical background (linear algebra, calculus, statistics)
            - Proficiency in Python, PyTorch, TensorFlow
            - Experience with deep learning and neural networks
            - Track record of publications in top venues
            
            Nice to Have:
            - Experience with large language models
            - Knowledge of reinforcement learning
            - Experience with distributed training
            - Understanding of AI safety and alignment
            - Experience with multimodal AI systems
            """
        }

# setup.py
"""
Setup script for Career Skills Gap Analyzer
Run this script to initialize the application with sample data
"""

import os
import sys
from pathlib import Path
from config import Config

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        Config.COMPANY_DATA_PATH,
        "faiss_index",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_sample_job_descriptions():
    """Create sample job descriptions if they don't exist"""
    company_data_path = Path(Config.COMPANY_DATA_PATH)
    
    if not any(company_data_path.glob("*.txt")):
        print("📝 Creating sample job descriptions...")
        
        sample_jobs = Config.get_sample_job_descriptions()
        
        for filename, content in sample_jobs.items():
            file_path = company_data_path / f"{filename}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created: {file_path}")
    else:
        print("✅ Job descriptions already exist")

def create_env_template():
    """Create .env template file"""
    env_template = """# Google AI API Key
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_AI_API_KEY=your_api_key_here

# Optional: Set custom paths
# COMPANY_DATA_PATH=company_data
# VECTOR_STORE_PATH=faiss_index
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_template)
        print("✅ Created .env template file")
        print("⚠️  Please add your Google AI API key to the .env file")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 Setting up Career Skills Gap Analyzer...")
    print("=" * 50)
    
    # Create directory structure
    create_directory_structure()
    
    # Create sample data
    create_sample_job_descriptions()
    
    # Create environment template
    create_env_template()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Add your Google AI API key to the .env file")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the app: streamlit run app.py")
    print("\nOptional:")
    print("- Add more job descriptions to the company_data/ folder")
    print("- Customize configuration in config.py")

if __name__ == "__main__":
    main()

# utils.py
"""
Utility functions for the Career Skills Gap Analyzer
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillExtractor:
    """Utility class for extracting skills from text"""
    
    # Common technical skills patterns
    TECH_SKILLS_PATTERNS = [
        r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Swift|Kotlin)\b',
        r'\b(?:React|Vue|Angular|Django|Flask|Spring|Express|Node\.js)\b',
        r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git)\b',
        r'\b(?:SQL|MongoDB|PostgreSQL|Redis|Elasticsearch)\b',
        r'\b(?:TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy)\b',
        r'\b(?:HTML|CSS|SCSS|Bootstrap|Tailwind)\b'
    ]
    
    # Soft skills keywords
    SOFT_SKILLS = [
        'communication', 'leadership', 'teamwork', 'problem-solving',
        'analytical thinking', 'creativity', 'adaptability', 'time management',
        'project management', 'presentation', 'collaboration', 'mentoring'
    ]
    
    @classmethod
    def extract_technical_skills(cls, text: str) -> List[str]:
        """Extract technical skills using regex patterns"""
        skills = set()
        
        for pattern in cls.TECH_SKILLS_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        
        return list(skills)
    
    @classmethod
    def extract_soft_skills(cls, text: str) -> List[str]:
        """Extract soft skills using keyword matching"""
        skills = []
        text_lower = text.lower()
        
        for skill in cls.SOFT_SKILLS:
            if skill in text_lower:
                skills.append(skill.title())
        
        return skills

class ProgressTracker:
    """Utility class for tracking learning progress"""
    
    def __init__(self):
        self.progress_data = {}
    
    def initialize_progress(self, roadmap: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize progress tracking for a roadmap"""
        weekly_plan = roadmap.get('weekly_plan', [])
        progress = {}
        
        for week in weekly_plan:
            week_num = week['week']
            activities = week.get('activities', [])
            
            progress[f"week_{week_num}"] = {
                'completed': False,
                'activities_completed': 0,
                'total_activities': len(activities),
                'hours_completed': 0,
                'total_hours': sum(a.get('estimated_hours', 0) for a in activities)
            }
        
        return progress
    
    def update_progress(self, week: int, activity_index: int, hours: float):
        """Update progress for a specific activity"""
        week_key = f"week_{week}"
        if week_key in self.progress_data:
            self.progress_data[week_key]['activities_completed'] += 1
            self.progress_data[week_key]['hours_completed'] += hours
            
            # Check if week is completed
            total_activities = self.progress_data[week_key]['total_activities']
            completed_activities = self.progress_data[week_key]['activities_completed']
            
            if completed_activities >= total_activities:
                self.progress_data[week_key]['completed'] = True
    
    def get_overall_progress(self) -> float:
        """Calculate overall progress percentage"""
        if not self.progress_data:
            return 0.0
        
        completed_weeks = sum(1 for week_data in self.progress_data.values() if week_data['completed'])
        total_weeks = len(self.progress_data)
        
        return (completed_weeks / total_weeks) * 100 if total_weeks > 0 else 0.0

class DataValidator:
    """Utility class for validating data structures"""
    
    @staticmethod
    def validate_skills_data(skills_data: Dict[str, List[str]]) -> bool:
        """Validate skills data structure"""
        required_keys = ['technical_skills', 'soft_skills', 'domain_knowledge']
        
        if not isinstance(skills_data, dict):
            return False
        
        for key in required_keys:
            if key not in skills_data:
                return False
            if not isinstance(skills_data[key], list):
                return False
        
        return True
    
    @staticmethod
    def validate_requirements_data(requirements: Dict[str, Any]) -> bool:
        """Validate role requirements data structure"""
        required_keys = ['required_skills', 'nice_to_have', 'responsibilities']
        
        if not isinstance(requirements, dict):
            return False
        
        for key in required_keys:
            if key not in requirements:
                return False
            if not isinstance(requirements[key], list):
                return False
        
        return True
    
    @staticmethod
    def validate_gap_analysis(gap_analysis: Dict[str, Any]) -> bool:
        """Validate gap analysis data structure"""
        required_keys = ['critical_gaps', 'intermediate_gaps', 'strengths', 'bonus_skills']
        
        if not isinstance(gap_analysis, dict):
            return False
        
        for key in required_keys:
            if key not in gap_analysis:
                return False
        
        return True

class JSONHandler:
    """Utility class for handling JSON operations"""
    
    @staticmethod
    def safe_json_parse(json_string: str) -> Optional[Dict[str, Any]]:
        """Safely parse JSON string with error handling"""
        try:
            # Clean the JSON string
            json_string = json_string.strip()
            
            # Remove any markdown code block markers
            if json_string.startswith('```json'):
                json_string = json_string[7:]
            if json_string.endswith('```'):
                json_string = json_string[:-3]
            
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {e}")
            return None
    
    @staticmethod
    def save_json(data: Dict[str, Any], filepath: str) -> bool:
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {filepath}: {e}")
            return False
    
    @staticmethod
    def load_json(filepath: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"File not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {filepath}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading JSON from {filepath}: {e}")
            return None

class StreamlitHelpers:
    """Utility functions for Streamlit UI components"""
    
    @staticmethod
    def display_skills_badges(skills: List[str], color: str = "blue"):
        """Display skills as badges"""
        if skills:
            for skill in skills:
                st.markdown(
                    f'<span style="background-color: {color}; color: white; '
                    f'padding: 2px 8px; border-radius: 12px; margin: 2px; '
                    f'display: inline-block; font-size: 12px;">{skill}</span>',
                    unsafe_allow_html=True
                )
    
    @staticmethod
    def create_progress_chart(progress_data: Dict[str, Any]):
        """Create a progress visualization chart"""
        import plotly.graph_objects as go
        
        weeks = []
        progress_values = []
        
        for week_key, week_data in progress_data.items():
            week_num = int(week_key.split('_')[1])
            weeks.append(f"Week {week_num}")
            
            if week_data['total_activities'] > 0:
                progress = (week_data['activities_completed'] / week_data['total_activities']) * 100
            else:
                progress = 0
            
            progress_values.append(progress)
        
        fig = go.Figure(data=go.Bar(
            x=weeks,
            y=progress_values,
            marker_color=['green' if p == 100 else 'orange' if p > 0 else 'lightgray' for p in progress_values]
        ))
        
        fig.update_layout(
            title="Learning Progress by Week",
            xaxis_title="Week",
            yaxis_title="Progress (%)",
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    @staticmethod
    def display_error_message(message: str, error_type: str = "error"):
        """Display formatted error messages"""
        if error_type == "error":
            st.error(f"❌ {message}")
        elif error_type == "warning":
            st.warning(f"⚠️ {message}")
        elif error_type == "info":
            st.info(f"ℹ️ {message}")
    
    @staticmethod
    def create_download_button(data: Dict[str, Any], filename: str, label: str):
        """Create a download button for JSON data"""
        json_string = json.dumps(data, indent=2)
        st.download_button(
            label=label,
            data=json_string,
            file_name=filename,
            mime="application/json"
        )