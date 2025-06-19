import os
import json
import tempfile
import base64
from typing import Dict, List, Tuple, Optional
import pandas as pd
import streamlit as st
import plotly.express as px
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import MessagesPlaceholder

DEFAULT_JOB_ROLES = [
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Research Scientist",
    "Data Engineer",
    "MLOps Engineer",
    "Full Stack Developer",
    "Cloud Architect",
    "DevOps Engineer"
]

SKILL_CATEGORIES = {
    "Technical": ["Programming", "ML Frameworks", "Cloud", "Databases", "DevOps"],
    "Soft": ["Communication", "Leadership", "Problem Solving", "Teamwork"]
}

def load_credentials() -> Dict[str, str]:
    try:
        return {
            "gemini_api_key": st.secrets["GEMINI_API_KEY"],
            "openai_api_key": st.secrets.get("OPENAI_API_KEY", "")
        }
    except (KeyError, FileNotFoundError) as e:
        st.error(f"""Missing API key: {e}. Please add it to .streamlit/secrets.toml with:
                GEMINI_API_KEY=your_key_here""")
        st.stop()

def display_pdf(file_path: str) -> None:
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def visualize_skill_gaps(skills_df: pd.DataFrame) -> None:
    skills_df = skills_df.rename(columns={
        'skill': 'Skill',
        'status': 'Status',
        'current_level': 'Level',
        'description': 'Description'
    })
    
    fig = px.bar(
        skills_df,
        x="Skill",
        y="Level",
        color="Status",
        title="Skill Gap Analysis",
        color_discrete_map={
            "Covered": "#2ecc71",
            "Moderate Gap": "#f39c12",
            "Critical Gap": "#e74c3c"
        },
        hover_data=["Description"]
    )
    fig.update_layout(
        xaxis_title="Skills",
        yaxis_title="Proficiency Level (1-5)",
        hovermode="closest"
    )
    st.plotly_chart(fig, use_container_width=True)

def parse_pdf(file_path: str) -> str:
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        return "\n".join([page.page_content for page in pages])
    except Exception as e:
        st.error(f"Error parsing PDF: {e}")
        return ""

def split_documents(text: str) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return text_splitter.create_documents([text])

def safe_json_parse(json_str: str) -> Dict:
    """Safely parse JSON with error handling and automatic correction"""
    try:
        # Try direct parsing first
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            # Try to extract JSON from markdown code block
            start_idx = json_str.find('{')
            end_idx = json_str.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                return json.loads(json_str[start_idx:end_idx])
            # Try to fix common formatting issues
            json_str = json_str.replace("'", '"')  # Replace single quotes
            json_str = json_str.replace("True", "true").replace("False", "false")  # Fix booleans
            json_str = json_str.replace("None", "null")  # Fix nulls
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse JSON: {e}\nOriginal content:\n{json_str}")
            return {}

class CareerRoadmapPlanner:
    def __init__(self):
        credentials = load_credentials()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            google_api_key=credentials["gemini_api_key"]
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=credentials["gemini_api_key"]
        )
        self.vectorstore = self._init_vectorstore()
        self.tools = self._init_tools()
        self.agent_executor = self._create_agent()

    def _init_vectorstore(self) -> FAISS:
        sample_jds = [
            Document(page_content="Data Scientist role requires Python, SQL, Machine Learning, Statistics. Senior level needs 5+ years experience.", 
                    metadata={"role": "Data Scientist"}),
            Document(page_content="ML Engineer needs Python, TensorFlow, PyTorch, Cloud (AWS/GCP), MLOps. Mid-level requires 3+ years.", 
                    metadata={"role": "Machine Learning Engineer"})
        ]
        return FAISS.from_documents(sample_jds, self.embeddings)

    def _init_tools(self) -> List[Tool]:
        @tool
        def analyze_resume(resume_text: str) -> Dict:
            """Analyze resume and extract skills, experience in JSON format."""
            prompt = ChatPromptTemplate.from_template(
                """Analyze this resume and extract skills in JSON format:
                {resume_text}
                
                Return JSON with structure:
                {{
                    "technical_skills": [{{"name": str, "proficiency": int (1-5)}}],
                    "soft_skills": [{{"name": str, "proficiency": int (1-5)}}],
                    "experience": [{{"role": str, "years": float, "description": str}}]
                }}"""
            )
            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({"resume_text": resume_text})
            return safe_json_parse(result)

        @tool
        def get_role_requirements(role: str) -> Dict:
            """Retrieve requirements for a specific job role using RAG."""
            prompt = ChatPromptTemplate.from_template(
                """What are the key requirements for a {role} position?
                
                Context: {context}
                
                Return JSON with:
                {{
                    "required_skills": [{{"name": str, "importance": str}}],
                    "experience_level": str,
                    "certifications": [str]
                }}"""
            )
            
            chain = (
                {
                    "context": lambda x: self.vectorstore.similarity_search(x["role"], k=3),
                    "role": RunnablePassthrough()
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )
            result = chain.invoke({"role": role})
            return safe_json_parse(result)

        @tool
        def analyze_gaps(user_skills: Dict, role_requirements: Dict, role: str) -> Dict:
            """Analyze skill gaps between user profile and role requirements."""
            prompt = ChatPromptTemplate.from_template(
                """Compare the user's skills with {role} requirements:
                
                User Skills: {user_skills}
                Role Requirements: {role_requirements}
                
                Return JSON with:
                {{
                    "skill_gaps": [{{
                        "skill": str,
                        "status": str,
                        "current_level": int,
                        "target_level": int,
                        "description": str
                    }}],
                    "summary": str
                }}"""
            )
            
            chain = (
                {
                    "user_skills": RunnablePassthrough(),
                    "role_requirements": RunnablePassthrough(),
                    "role": RunnablePassthrough()
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )
            result = chain.invoke({
                "user_skills": user_skills,
                "role_requirements": role_requirements,
                "role": role
            })
            return safe_json_parse(result)

        @tool
        def build_roadmap(name: str, target_role: str, current_skills: Dict, gap_analysis: Dict) -> Dict:
            """Create a personalized learning roadmap."""
            prompt = ChatPromptTemplate.from_template(
                """Create a 12-week learning roadmap for {name} transitioning to {target_role}.
                
                Current Skills: {current_skills}
                Skill Gaps: {skill_gaps}
                
                Format as JSON with:
                {{
                    "weeks": [{{"week": int, "topics": [str], "resources": [str], "project": str}}],
                    "milestones": [{{"week": int, "description": str}}]
                }}"""
            )
            
            chain = (
                {
                    "name": RunnablePassthrough(),
                    "target_role": RunnablePassthrough(),
                    "current_skills": RunnablePassthrough(),
                    "skill_gaps": RunnablePassthrough()
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )
            result = chain.invoke({
                "name": name,
                "target_role": target_role,
                "current_skills": current_skills,
                "skill_gaps": gap_analysis["skill_gaps"]  # Extract skill gaps list from gap_analysis dict
            })
            return safe_json_parse(result)

        return [
            analyze_resume,
            get_role_requirements,
            analyze_gaps,
            build_roadmap
        ]

    def _create_agent(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a career roadmap planner. Use tools to analyze resumes, get role requirements, analyze gaps, and build roadmaps."),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def analyze_resume(self, resume_text: str) -> Dict:
        return self.tools[0].invoke({"resume_text": resume_text})

    def get_role_requirements(self, role: str) -> Dict:
        return self.tools[1].invoke({"role": role})

    def analyze_gaps(self, user_skills: Dict, role_requirements: Dict, role: str) -> Dict:
        return self.tools[2].invoke({
            "user_skills": user_skills,
            "role_requirements": role_requirements,
            "role": role
        })

    def build_roadmap(self, name: str, target_role: str, current_skills: Dict, gap_analysis: Dict) -> Dict:
        return self.tools[3].invoke({
            "name": name,
            "target_role": target_role,
            "current_skills": current_skills,
            "gap_analysis": gap_analysis  # Pass the entire gap_analysis dict
        })

def setup_ui() -> None:
    st.set_page_config(
        page_title="AI Career Roadmap Planner",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
        .stApp { background-color: #f5f5f5; }
        .sidebar .sidebar-content { background-color: #2c3e50; }
        h1 { color: #3498db; }
        h2 { color: #2c3e50; }
        .stButton>button { background-color: #3498db; color: white; }
        .stTextInput>div>div>input { border: 1px solid #3498db; }
        .stDownloadButton>button { background-color: #2ecc71; color: white; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] { padding: 8px 16px; border-radius: 4px; }
        .stTabs [aria-selected="true"] { background-color: #3498db; color: white; }
    </style>
    """, unsafe_allow_html=True)

def show_header() -> None:
    st.title("AI-Powered Career Roadmap Planner")
    st.markdown("""
    **Upload your resume** and target job role to get a **personalized 12-week learning plan** 
    with skill gap analysis and milestone tracking.
    """)

def resume_input_section() -> Tuple[str, str, str]:
    with st.expander("📄 Upload Your Resume", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload PDF Resume",
                type=["pdf"],
                help="Upload your resume in PDF format"
            )
            resume_text = ""
            
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    resume_text = parse_pdf(tmp_file.name)
            
        with col2:
            linkedin_url = st.text_input(
                "Or enter LinkedIn profile URL",
                placeholder="https://linkedin.com/in/yourprofile",
                help="We'll only use this to extract your experience"
            )
            
            if linkedin_url:
                st.warning("Note: LinkedIn integration not implemented in this demo. Please upload PDF.")
        
        name = st.text_input("Your Name", placeholder="John Doe")
        target_role = st.selectbox(
            "Target Job Role",
            options=DEFAULT_JOB_ROLES,
            index=0,
            help="Select your desired career role"
        )
        
        return name, resume_text, target_role

def display_results(
    name: str,\
    target_role: str, 
    profile_analysis: Dict,
    role_requirements: Dict,
    gap_analysis: Dict,
    roadmap: Dict
) -> None:
    tab1, tab2, tab3 = st.tabs(["Profile Analysis", "Skill Gaps", "Learning Roadmap"])
    
    with tab1:
        st.subheader("📊 Your Current Skills Profile")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Technical Skills**")
            if "technical_skills" in profile_analysis:
                tech_skills_df = pd.DataFrame(profile_analysis["technical_skills"])
                st.dataframe(
                    tech_skills_df.style.background_gradient(cmap="Blues"),
                    use_container_width=True
                )
            else:
                st.warning("No technical skills found in analysis")
        
        with col2:
            st.markdown("**Soft Skills**")
            if "soft_skills" in profile_analysis:
                soft_skills_df = pd.DataFrame(profile_analysis["soft_skills"])
                st.dataframe(
                    soft_skills_df.style.background_gradient(cmap="Greens"),
                    use_container_width=True
                )
            else:
                st.warning("No soft skills found in analysis")
        
        st.markdown("**Work Experience**")
        if "experience" in profile_analysis:
            exp_df = pd.DataFrame(profile_analysis["experience"])
            st.dataframe(exp_df, use_container_width=True)
        else:
            st.warning("No work experience found in analysis")
    
    with tab2:
        st.subheader("🔍 Skill Gap Analysis")
        if "summary" in gap_analysis:
            st.markdown(f"**Summary:** {gap_analysis['summary']}")
        else:
            st.warning("No gap analysis summary found")
        
        if "skill_gaps" in gap_analysis:
            gaps_df = pd.DataFrame(gap_analysis["skill_gaps"])
            visualize_skill_gaps(gaps_df)
            
            st.markdown("**Detailed Gap Analysis**")
            st.dataframe(gaps_df, use_container_width=True)
        else:
            st.warning("No skill gaps data found")
    
    with tab3:
        st.subheader("🗺️ Personalized Learning Roadmap")
        
        if "experience_level" in role_requirements:
            st.success(f"Here's your 12-week plan to transition to {role_requirements['experience_level']} {target_role}")
        else:
            st.success(f"Here's your 12-week plan to transition to {target_role}")
        
        if "weeks" in roadmap:
            for week in roadmap["weeks"]:
                with st.expander(f"Week {week['week']}: {', '.join(week['topics'])}", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown("**Topics**")
                        for topic in week["topics"]:
                            st.markdown(f"- {topic}")
                    
                    with col2:
                        st.markdown("**Resources & Project**")
                        st.markdown("**Resources:**")
                        for resource in week["resources"]:
                            st.markdown(f"- {resource}")
                        
                        st.markdown(f"**Practical Project:** {week['project']}")
        else:
            st.warning("No roadmap weeks data found")
        
        st.markdown("**Key Milestones**")
        if "milestones" in roadmap:
            for milestone in roadmap["milestones"]:
                st.markdown(f"🏁 **Week {milestone['week']}:** {milestone['description']}")
        else:
            st.warning("No milestones found in roadmap")
        
        if roadmap:
            st.download_button(
                label="Download Roadmap (JSON)",
                data=json.dumps(roadmap, indent=2),
                file_name=f"{name}_career_roadmap.json",
                mime="application/json"
            )

def main():
    setup_ui()
    show_header()
    
    planner = CareerRoadmapPlanner()
    name, resume_text, target_role = resume_input_section()
    
    if st.button("Generate Career Roadmap") and resume_text:
        with st.spinner("Analyzing your profile and creating roadmap..."):
            try:
                profile_analysis = planner.analyze_resume(resume_text)
                role_requirements = planner.get_role_requirements(target_role)
                gap_analysis = planner.analyze_gaps(
                    profile_analysis,
                    role_requirements,
                    target_role
                )
                roadmap = planner.build_roadmap(
                    name,
                    target_role,
                    profile_analysis,
                    gap_analysis
                )
                
                # Pass all required arguments including roadmap
                display_results(
                    name,
                    target_role, 
                    profile_analysis,
                    role_requirements,
                    gap_analysis,
                    roadmap  # Make sure to include roadmap here
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    elif not resume_text:
        st.warning("Please upload your resume to proceed")

if __name__ == "__main__":
    main()