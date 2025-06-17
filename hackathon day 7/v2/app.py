import streamlit as st
import os
import json
import pickle
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
import re
from pathlib import Path

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.embeddings.google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.schema import Document

# PDF processing
import fitz  # PyMuPDF

# Configure page
st.set_page_config(
    page_title="AI Career Skills Gap Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'user_skills' not in st.session_state:
    st.session_state.user_skills = []
if 'role_requirements' not in st.session_state:
    st.session_state.role_requirements = {}
if 'gap_analysis' not in st.session_state:
    st.session_state.gap_analysis = {}
if 'roadmap' not in st.session_state:
    st.session_state.roadmap = {}

class SkillsAnalyzer:
    """Main orchestrator for the skills gap analysis system"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        self.vector_store = None
        
        # Initialize agents
        self.profile_analyzer = ProfileAnalyzerAgent(self.llm)
        self.role_retriever = RoleRequirementRetrieverAgent(self.llm, self.embeddings)
        self.gap_analyzer = GapAnalysisAgent(self.llm)
        self.roadmap_builder = RoadmapBuilderAgent(self.llm)
        
        # Load or create vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize FAISS vector store from company data"""
        vector_store_path = "faiss_index"
        company_data_path = "company_data"
        
        if os.path.exists(vector_store_path):
            # Load existing vector store
            try:
                self.vector_store = FAISS.load_local(
                    vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                st.success("✅ Loaded existing job descriptions database")
            except Exception as e:
                st.warning(f"Could not load existing vector store: {e}")
                self._create_vector_store()
        else:
            self._create_vector_store()
    
    def _create_vector_store(self):
        """Create new vector store from company data folder"""
        company_data_path = "company_data"
        
        if not os.path.exists(company_data_path):
            os.makedirs(company_data_path)
            # Create sample job descriptions
            self._create_sample_data()
        
        documents = []
        
        # Load all text files from company_data folder
        for file_path in Path(company_data_path).glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={"source": file_path.stem, "company": file_path.stem.split('_')[0]}
                    )
                    documents.append(doc)
            except Exception as e:
                st.warning(f"Could not load {file_path}: {e}")
        
        if documents:
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
            
            # Save vector store
            self.vector_store.save_local("faiss_index")
            st.success(f"✅ Created vector database with {len(documents)} job descriptions")
        else:
            st.error("❌ No job descriptions found in company_data folder")
    
    def _create_sample_data(self):
        """Create sample job descriptions for demonstration"""
        sample_jobs = {
            "google_ml_engineer": """
            Google - Machine Learning Engineer
            
            Responsibilities:
            - Design and implement machine learning models at scale
            - Work with TensorFlow, PyTorch, and Google Cloud ML
            - Develop MLOps pipelines and model deployment strategies
            - Collaborate with cross-functional teams on AI products
            
            Required Skills:
            - 3+ years experience in machine learning
            - Proficiency in Python, TensorFlow, PyTorch
            - Knowledge of statistics, linear algebra, calculus
            - Experience with cloud platforms (GCP preferred)
            - Strong programming and software engineering skills
            
            Nice to Have:
            - PhD in Computer Science, Statistics, or related field
            - Experience with large-scale distributed systems
            - Knowledge of MLOps tools (Kubeflow, MLflow)
            - Publications in ML conferences
            """,
            
            "microsoft_data_scientist": """
            Microsoft - Senior Data Scientist
            
            Responsibilities:
            - Build predictive models for business intelligence
            - Analyze large datasets using SQL, Python, R
            - Create data visualizations and reports
            - Present findings to stakeholders and leadership
            
            Required Skills:
            - 5+ years experience in data science
            - Expert in Python, R, SQL
            - Knowledge of statistical modeling and hypothesis testing
            - Experience with Azure cloud services
            - Strong communication and presentation skills
            
            Nice to Have:
            - Master's degree in Data Science, Statistics, or related
            - Experience with deep learning frameworks
            - Knowledge of business domain expertise
            - Certification in Azure Data Science
            """,
            
            "amazon_software_engineer": """
            Amazon - Software Development Engineer
            
            Responsibilities:
            - Design and develop scalable web applications
            - Write clean, maintainable code in Java, Python, or JavaScript
            - Participate in code reviews and system design discussions
            - Work in agile development environment
            
            Required Skills:
            - 2+ years software development experience
            - Proficiency in at least one programming language (Java, Python, C++)
            - Understanding of data structures and algorithms
            - Experience with web development frameworks
            - Knowledge of database systems (SQL, NoSQL)
            
            Nice to Have:
            - Bachelor's degree in Computer Science
            - Experience with AWS cloud services
            - Knowledge of microservices architecture
            - Experience with containerization (Docker, Kubernetes)
            """
        }
        
        company_data_path = "company_data"
        for filename, content in sample_jobs.items():
            with open(f"{company_data_path}/{filename}.txt", 'w', encoding='utf-8') as f:
                f.write(content)

class ProfileAnalyzerAgent:
    """Agent responsible for analyzing user profiles and extracting skills"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def analyze_profile(self, profile_text: str) -> Dict[str, List[str]]:
        """Extract skills from profile text"""
        prompt = f"""
        Analyze the following resume/profile and extract skills. Categorize them as:
        1. Technical Skills (programming languages, frameworks, tools, technologies)
        2. Soft Skills (communication, leadership, problem-solving, etc.)
        3. Domain Knowledge (industry-specific knowledge, certifications)
        
        Profile Text:
        {profile_text}
        
        Return the response in the following JSON format:
        {{
            "technical_skills": ["skill1", "skill2", ...],
            "soft_skills": ["skill1", "skill2", ...],
            "domain_knowledge": ["skill1", "skill2", ...]
        }}
        
        Only return valid JSON, no additional text.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            # Parse JSON response
            skills_data = json.loads(response.content)
            return skills_data
        except Exception as e:
            st.error(f"Error analyzing profile: {e}")
            return {"technical_skills": [], "soft_skills": [], "domain_knowledge": []}
    
    def extract_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        try:
            # Save uploaded file temporarily
            with open("temp_resume.pdf", "wb") as f:
                f.write(pdf_file.getvalue())
            
            # Extract text using PyMuPDF
            doc = fitz.open("temp_resume.pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            # Clean up temp file
            os.remove("temp_resume.pdf")
            
            return text
        except Exception as e:
            st.error(f"Error extracting PDF text: {e}")
            return ""

class RoleRequirementRetrieverAgent:
    """Agent for retrieving role requirements using RAG"""
    
    def __init__(self, llm, embeddings):
        self.llm = llm
        self.embeddings = embeddings
    
    def retrieve_requirements(self, query: str, vector_store, top_k: int = 3) -> Dict[str, Any]:
        """Retrieve role requirements using RAG"""
        if not vector_store:
            return {"required_skills": [], "nice_to_have": [], "responsibilities": []}
        
        try:
            # Search for relevant job descriptions
            docs = vector_store.similarity_search(query, k=top_k)
            
            # Combine retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            prompt = f"""
            Based on the following job descriptions, extract the role requirements:
            
            Job Descriptions:
            {context}
            
            Extract and categorize the requirements into:
            1. Required Skills (must-have technical and soft skills)
            2. Nice to Have (preferred but not mandatory skills)
            3. Key Responsibilities (main job duties)
            
            Return in JSON format:
            {{
                "required_skills": ["skill1", "skill2", ...],
                "nice_to_have": ["skill1", "skill2", ...],
                "responsibilities": ["responsibility1", "responsibility2", ...]
            }}
            
            Only return valid JSON, no additional text.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            requirements = json.loads(response.content)
            
            # Add source information
            requirements["sources"] = [doc.metadata.get("source", "Unknown") for doc in docs]
            
            return requirements
            
        except Exception as e:
            st.error(f"Error retrieving requirements: {e}")
            return {"required_skills": [], "nice_to_have": [], "responsibilities": [], "sources": []}

class GapAnalysisAgent:
    """Agent for performing skills gap analysis"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def analyze_gaps(self, user_skills: Dict[str, List[str]], role_requirements: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze skill gaps between user profile and role requirements"""
        prompt = f"""
        Perform a detailed skills gap analysis between the user's current skills and role requirements.
        
        User's Current Skills:
        Technical Skills: {user_skills.get('technical_skills', [])}
        Soft Skills: {user_skills.get('soft_skills', [])}
        Domain Knowledge: {user_skills.get('domain_knowledge', [])}
        
        Role Requirements:
        Required Skills: {role_requirements.get('required_skills', [])}
        Nice to Have: {role_requirements.get('nice_to_have', [])}
        
        Analyze and categorize the gaps:
        1. Critical Gaps: Required skills the user lacks
        2. Intermediate Gaps: Nice-to-have skills that would strengthen the application
        3. Strengths: Skills the user has that match requirements
        4. Bonus Skills: User skills that exceed requirements
        
        For each gap, provide a brief explanation of why it's important.
        
        Return in JSON format:
        {{
            "critical_gaps": [
                {{"skill": "skill_name", "importance": "explanation"}}, ...
            ],
            "intermediate_gaps": [
                {{"skill": "skill_name", "importance": "explanation"}}, ...
            ],
            "strengths": [
                {{"skill": "skill_name", "match_level": "exact/partial"}}, ...
            ],
            "bonus_skills": ["skill1", "skill2", ...],
            "overall_match_percentage": 75
        }}
        
        Only return valid JSON, no additional text.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            gap_analysis = json.loads(response.content)
            return gap_analysis
        except Exception as e:
            st.error(f"Error analyzing gaps: {e}")
            return {
                "critical_gaps": [],
                "intermediate_gaps": [],
                "strengths": [],
                "bonus_skills": [],
                "overall_match_percentage": 0
            }

class RoadmapBuilderAgent:
    """Agent for building learning roadmaps"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def build_roadmap(self, gap_analysis: Dict[str, Any], timeframe_weeks: int = 12) -> Dict[str, Any]:
        """Build a learning roadmap based on gap analysis"""
        prompt = f"""
        Create a detailed learning roadmap to address the identified skill gaps within {timeframe_weeks} weeks.
        
        Gap Analysis:
        Critical Gaps: {gap_analysis.get('critical_gaps', [])}
        Intermediate Gaps: {gap_analysis.get('intermediate_gaps', [])}
        
        Create a week-by-week learning plan that:
        1. Prioritizes critical gaps first
        2. Includes specific learning resources and activities
        3. Has measurable milestones
        4. Balances theoretical learning with practical application
        5. Includes time estimates for each activity
        
        Return in JSON format:
        {{
            "roadmap_overview": {{
                "total_weeks": {timeframe_weeks},
                "focus_areas": ["area1", "area2", ...],
                "estimated_hours_per_week": 15
            }},
            "weekly_plan": [
                {{
                    "week": 1,
                    "focus": "Week focus description",
                    "skills_to_learn": ["skill1", "skill2"],
                    "activities": [
                        {{
                            "activity": "Activity description",
                            "resource": "Recommended resource",
                            "estimated_hours": 5,
                            "outcome": "Expected outcome"
                        }}
                    ],
                    "milestone": "Week completion milestone"
                }}
            ],
            "milestones": [
                {{
                    "week": 4,
                    "title": "Milestone title",
                    "description": "Milestone description",
                    "deliverable": "What to complete"
                }}
            ]
        }}
        
        Only return valid JSON, no additional text.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            roadmap = json.loads(response.content)
            return roadmap
        except Exception as e:
            st.error(f"Error building roadmap: {e}")
            return {
                "roadmap_overview": {"total_weeks": timeframe_weeks, "focus_areas": [], "estimated_hours_per_week": 0},
                "weekly_plan": [],
                "milestones": []
            }

def main():
    st.title("🎯 AI Career Skills Gap Analyzer")
    st.markdown("**Accelerate your career with AI-powered skill gap analysis and personalized learning roadmaps**")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Google AI API Key",
            type="password",
            help="Get your API key from https://makersuite.google.com/app/apikey"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your Google AI API key to continue")
            st.stop()
        
        st.success("✅ API Key configured")
        
        # Initialize analyzer
        if 'analyzer' not in st.session_state:
            with st.spinner("Initializing AI system..."):
                st.session_state.analyzer = SkillsAnalyzer(api_key)
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Profile Analysis", "🎯 Role Requirements", "📊 Gap Analysis", "🛣️ Learning Roadmap"])
    
    # Tab 1: Profile Analysis
    with tab1:
        st.header("📝 Profile Analysis")
        st.markdown("Upload your resume or enter your profile information to extract your current skills.")
        
        input_method = st.radio("Choose input method:", ["Upload PDF Resume", "Enter Text Manually"])
        
        profile_text = ""
        
        if input_method == "Upload PDF Resume":
            uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
            if uploaded_file:
                with st.spinner("Extracting text from PDF..."):
                    profile_text = st.session_state.analyzer.profile_analyzer.extract_from_pdf(uploaded_file)
                    st.text_area("Extracted Text Preview", profile_text[:1000] + "...", height=200, disabled=True)
        else:
            profile_text = st.text_area(
                "Enter your profile information:",
                placeholder="Paste your resume content, LinkedIn profile, or describe your skills and experience...",
                height=300
            )
        
        if st.button("🔍 Analyze Profile", type="primary") and profile_text:
            with st.spinner("Analyzing your profile..."):
                skills = st.session_state.analyzer.profile_analyzer.analyze_profile(profile_text)
                st.session_state.user_skills = skills
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("💻 Technical Skills")
                    for skill in skills.get('technical_skills', []):
                        st.write(f"• {skill}")
                
                with col2:
                    st.subheader("🤝 Soft Skills")
                    for skill in skills.get('soft_skills', []):
                        st.write(f"• {skill}")
                
                with col3:
                    st.subheader("📚 Domain Knowledge")
                    for skill in skills.get('domain_knowledge', []):
                        st.write(f"• {skill}")
                
                st.success("✅ Profile analysis complete!")
    
    # Tab 2: Role Requirements
    with tab2:
        st.header("🎯 Role Requirements")
        st.markdown("Search for role requirements from our job descriptions database.")
        
        # Role search
        role_query = st.text_input(
            "Search for roles:",
            placeholder="e.g., 'Machine Learning Engineer', 'Data Scientist', 'Software Engineer'"
        )
        
        if st.button("🔍 Search Role Requirements", type="primary") and role_query:
            with st.spinner("Searching job requirements..."):
                requirements = st.session_state.analyzer.role_retriever.retrieve_requirements(
                    role_query, 
                    st.session_state.analyzer.vector_store
                )
                st.session_state.role_requirements = requirements
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ Required Skills")
                    for skill in requirements.get('required_skills', []):
                        st.write(f"• {skill}")
                
                with col2:
                    st.subheader("⭐ Nice to Have")
                    for skill in requirements.get('nice_to_have', []):
                        st.write(f"• {skill}")
                
                st.subheader("📋 Key Responsibilities")
                for resp in requirements.get('responsibilities', []):
                    st.write(f"• {resp}")
                
                if requirements.get('sources'):
                    st.info(f"📍 Sources: {', '.join(requirements['sources'])}")
                
                st.success("✅ Role requirements retrieved!")
    
    # Tab 3: Gap Analysis
    with tab3:
        st.header("📊 Skills Gap Analysis")
        
        if st.session_state.user_skills and st.session_state.role_requirements:
            if st.button("🔍 Perform Gap Analysis", type="primary"):
                with st.spinner("Analyzing skill gaps..."):
                    gap_analysis = st.session_state.analyzer.gap_analyzer.analyze_gaps(
                        st.session_state.user_skills,
                        st.session_state.role_requirements
                    )
                    st.session_state.gap_analysis = gap_analysis
                    
                    # Display overall match
                    match_pct = gap_analysis.get('overall_match_percentage', 0)
                    st.metric("Overall Match", f"{match_pct}%")
                    st.progress(match_pct / 100)
                    
                    # Display gaps and strengths
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🚨 Critical Gaps")
                        for gap in gap_analysis.get('critical_gaps', []):
                            st.error(f"**{gap['skill']}**")
                            st.write(gap['importance'])
                        
                        st.subheader("⚠️ Intermediate Gaps")
                        for gap in gap_analysis.get('intermediate_gaps', []):
                            st.warning(f"**{gap['skill']}**")
                            st.write(gap['importance'])
                    
                    with col2:
                        st.subheader("✅ Your Strengths")
                        for strength in gap_analysis.get('strengths', []):
                            st.success(f"**{strength['skill']}** ({strength['match_level']} match)")
                        
                        st.subheader("🌟 Bonus Skills")
                        for skill in gap_analysis.get('bonus_skills', []):
                            st.info(f"• {skill}")
                    
                    st.session_state.analysis_complete = True
                    st.success("✅ Gap analysis complete!")
        else:
            st.warning("⚠️ Please complete Profile Analysis and Role Requirements first.")
    
    # Tab 4: Learning Roadmap
    with tab4:
        st.header("🛣️ Learning Roadmap")
        
        if st.session_state.gap_analysis:
            # Roadmap configuration
            col1, col2 = st.columns(2)
            with col1:
                timeframe = st.slider("Learning timeframe (weeks)", 4, 24, 12)
            with col2:
                st.metric("Estimated hours/week", "10-20")
            
            if st.button("🚀 Generate Learning Roadmap", type="primary"):
                with st.spinner("Creating your personalized roadmap..."):
                    roadmap = st.session_state.analyzer.roadmap_builder.build_roadmap(
                        st.session_state.gap_analysis, 
                        timeframe
                    )
                    st.session_state.roadmap = roadmap
                    
                    # Display roadmap overview
                    overview = roadmap.get('roadmap_overview', {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Weeks", overview.get('total_weeks', 0))
                    with col2:
                        st.metric("Focus Areas", len(overview.get('focus_areas', [])))
                    with col3:
                        st.metric("Hours/Week", overview.get('estimated_hours_per_week', 0))
                    
                    # Display focus areas
                    st.subheader("🎯 Focus Areas")
                    focus_areas = overview.get('focus_areas', [])
                    if focus_areas:
                        st.write(", ".join(focus_areas))
                    
                    # Weekly plan visualization
                    st.subheader("📅 Weekly Learning Plan")
                    
                    weekly_plan = roadmap.get('weekly_plan', [])
                    if weekly_plan:
                        # Create progress tracking
                        weeks_data = []
                        for week in weekly_plan:
                            total_hours = sum(activity.get('estimated_hours', 0) for activity in week.get('activities', []))
                            weeks_data.append({
                                'Week': f"Week {week['week']}",
                                'Hours': total_hours,
                                'Focus': week.get('focus', 'N/A')
                            })
                        
                        df = pd.DataFrame(weeks_data)
                        fig = px.bar(df, x='Week', y='Hours', title='Weekly Time Investment')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Detailed weekly breakdown
                        for week in weekly_plan[:4]:  # Show first 4 weeks in detail
                            with st.expander(f"Week {week['week']}: {week.get('focus', 'Focus TBD')}"):
                                st.write(f"**Skills to Learn:** {', '.join(week.get('skills_to_learn', []))}")
                                
                                st.write("**Activities:**")
                                for activity in week.get('activities', []):
                                    st.write(f"• **{activity.get('activity', 'N/A')}** ({activity.get('estimated_hours', 0)}h)")
                                    st.write(f"  Resource: {activity.get('resource', 'N/A')}")
                                    st.write(f"  Outcome: {activity.get('outcome', 'N/A')}")
                                
                                st.write(f"**Week Milestone:** {week.get('milestone', 'N/A')}")
                    
                    # Major milestones
                    st.subheader("🏆 Major Milestones")
                    milestones = roadmap.get('milestones', [])
                    if milestones:
                        for milestone in milestones:
                            st.success(f"**Week {milestone['week']}: {milestone['title']}**")
                            st.write(milestone['description'])
                            st.write(f"Deliverable: {milestone['deliverable']}")
                    
                    st.success("✅ Learning roadmap generated!")
        else:
            st.warning("⚠️ Please complete the Gap Analysis first.")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit, LangChain, Gemini AI, and FAISS")

if __name__ == "__main__":
    main()