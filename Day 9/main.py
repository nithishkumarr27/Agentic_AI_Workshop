import os
import json
import tempfile
import base64
import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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

# Configuration
JD_DIRECTORY = "job_descriptions"  # Directory containing sample job description PDFs
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

def visualize_roadmap_progress(roadmap: Dict) -> None:
    if not roadmap or 'weeks' not in roadmap:
        st.warning("No roadmap data available for visualization")
        return
    
    # Create progress data
    tasks = []
    today = datetime.date.today()
    
    for week in roadmap['weeks']:
        week_num = week['week']
        status = st.session_state.progress.get(week_num, "Not Started")
        
        # Calculate dates for the week
        start_date = today + datetime.timedelta(days=(week_num-1)*7)
        end_date = start_date + datetime.timedelta(days=6)
        
        tasks.append({
            'Task': f"Week {week_num}",
            'Start': start_date,
            'Finish': end_date,
            'Status': status
        })
    
    # Create Gantt chart
    fig = px.timeline(
        pd.DataFrame(tasks),
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Status",
        color_discrete_map={
            "Completed": "#2ecc71",
            "In Progress": "#f39c12",
            "Not Started": "#e74c3c"
        },
        title="Learning Roadmap Progress"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Timeline",
        yaxis_title="Week",
        height=500
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

def load_jd_documents(directory: str) -> List[Document]:
    """Load all PDF job descriptions from a directory"""
    documents = []
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith(".pdf"):
                filepath = os.path.join(directory, filename)
                try:
                    loader = PyPDFLoader(filepath)
                    pages = loader.load()
                    role = filename.replace(".pdf", "").replace("_", " ")
                    for page in pages:
                        page.metadata["role"] = role
                        page.metadata["source"] = "sample"
                    documents.extend(pages)
                except Exception as e:
                    st.error(f"Error loading {filename}: {e}")
    else:
        st.warning(f"JD directory not found: {directory}")
    return documents

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
        """Initialize vector store with job descriptions from directory"""
        documents = load_jd_documents(JD_DIRECTORY)
        if not documents:
            st.warning("No job descriptions found. Using empty vector store.")
        return FAISS.from_documents(documents, self.embeddings)

    def add_jd_to_vectorstore(self, jd_text: str, role: str) -> None:
        """Add new job description to vector store"""
        doc = Document(
            page_content=jd_text,
            metadata={"role": role, "source": "user"}
        )
        self.vectorstore.add_documents([doc])
        st.success(f"Added new JD for {role} to knowledge base!")

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
            # Retrieve most relevant documents
            docs = self.vectorstore.similarity_search(role, k=3)
            context = "\n\n".join([d.page_content for d in docs])
            
            prompt = ChatPromptTemplate.from_template(
                """Based on the following job descriptions, extract key requirements for a {role} position:
                
                Context:
                {context}
                
                Return JSON with:
                {{
                    "role": str,
                    "required_skills": [{{"name": str, "importance": "Critical"|"Important"|"Nice-to-have"}}],
                    "experience_level": str,
                    "certifications": [str],
                    "education": str,
                    "source": str
                }}"""
            )
            
            chain = (
                {
                    "context": RunnableLambda(lambda x: context),
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
                
                User Skills: 
                {user_skills}
                
                Role Requirements: 
                {role_requirements}
                
                Return JSON with:
                {{
                    "role": str,
                    "skill_gaps": [{{
                        "skill": str,
                        "status": "Covered"|"Moderate Gap"|"Critical Gap",
                        "current_level": int,
                        "target_level": int,
                        "description": str
                    }}],
                    "summary": str
                }}"""
            )
            
            chain = (
                {
                    "user_skills": RunnableLambda(lambda x: json.dumps(x)),
                    "role_requirements": RunnableLambda(lambda x: json.dumps(x)),
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
                
                Current Skills: 
                {current_skills}
                
                Skill Gaps: 
                {skill_gaps}
                
                Format as JSON with:
                {{
                    "name": str,
                    "target_role": str,
                    "start_date": "YYYY-MM-DD",
                    "weeks": [{{
                        "week": int,
                        "focus_areas": [str],
                        "topics": [str],
                        "resources": [str],
                        "project": str,
                        "milestone": bool
                    }}],
                    "milestones": [{{"week": int, "description": str}}]
                }}"""
            )
            
            chain = (
                {
                    "name": RunnablePassthrough(),
                    "target_role": RunnablePassthrough(),
                    "current_skills": RunnableLambda(lambda x: json.dumps(x)),
                    "skill_gaps": RunnableLambda(lambda x: json.dumps(x["skill_gaps"]))
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )
            result = chain.invoke({
                "name": name,
                "target_role": target_role,
                "current_skills": current_skills,
                "skill_gaps": gap_analysis
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
            "gap_analysis": gap_analysis
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
        .status-badge {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin-left: 10px;
        }
        .completed { background-color: #2ecc71; color: white; }
        .in-progress { background-color: #f39c12; color: white; }
        .not-started { background-color: #e74c3c; color: white; }
    </style>
    """, unsafe_allow_html=True)

def show_header() -> None:
    st.title("AI-Powered Career Roadmap Planner")
    st.markdown("""
    **Upload your resume** and target job role to get a **personalized 12-week learning plan** 
    with skill gap analysis and milestone tracking.
    """)
    st.divider()

def resume_input_section(planner: CareerRoadmapPlanner) -> Tuple[str, str, str]:
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
        
        # JD Upload Section
        st.subheader("🔍 Job Description Source")
        jd_option = st.radio(
            "Select JD source:",
            ["Use sample JDs", "Upload custom JD"],
            horizontal=True
        )
        
        jd_text = ""
        if jd_option == "Upload custom JD":
            jd_file = st.file_uploader(
                "Upload Job Description (PDF or TXT)",
                type=["pdf", "txt"],
                help="Upload the job description you're targeting"
            )
            
            if jd_file is not None:
                if jd_file.type == "application/pdf":
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(jd_file.getvalue())
                        jd_text = parse_pdf(tmp_file.name)
                else:
                    jd_text = jd_file.getvalue().decode("utf-8")
                
                if jd_text:
                    planner.add_jd_to_vectorstore(jd_text, target_role)
        
        return name, resume_text, target_role

def display_roadmap_with_progress(roadmap: Dict) -> None:
    if not roadmap or 'weeks' not in roadmap:
        st.warning("Roadmap data not available")
        return
    
    # Initialize session state for progress tracking
    if 'progress' not in st.session_state:
        st.session_state.progress = {}
        for week in roadmap['weeks']:
            week_num = week['week']
            st.session_state.progress[week_num] = "Not Started"
    
    st.subheader("🗺️ Personalized Learning Roadmap")
    st.caption(f"Roadmap for {roadmap.get('name', 'User')} to become a {roadmap.get('target_role', 'target role')}")
    
    # Visualize progress
    visualize_roadmap_progress(roadmap)
    
    # Weekly breakdown with status tracking
    for week in roadmap['weeks']:
        week_num = week['week']
        status = st.session_state.progress.get(week_num, "Not Started")
        
        # Create custom header with status badge
        col1, col2 = st.columns([1, 0.2])
        with col1:
            st.subheader(f"Week {week_num}: {', '.join(week.get('focus_areas', []))}")
        with col2:
            # Status indicator
            status_text = ""
            if status == "Completed":
                status_text = "✅ Completed"
            elif status == "In Progress":
                status_text = "🔄 In Progress"
            else:
                status_text = "❌ Not Started"
            st.markdown(f"**{status_text}**")
        
        with st.expander("View details", expanded=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Topics to Learn**")
                for topic in week.get('topics', []):
                    st.markdown(f"- {topic}")
                
                st.markdown("**Resources**")
                for resource in week.get('resources', []):
                    st.markdown(f"- {resource}")
            
            with col2:
                if week.get('project'):
                    st.markdown("**Practical Project**")
                    st.info(week['project'])
                
                if week.get('milestone'):
                    st.markdown("**Milestone Achievement**")
                    st.success(week['milestone'])
            
            # Status selector
            new_status = st.selectbox(
                f"Update status for Week {week_num}",
                ["Not Started", "In Progress", "Completed"],
                index=["Not Started", "In Progress", "Completed"].index(status),
                key=f"status_{week_num}"
            )
            
            if new_status != status:
                st.session_state.progress[week_num] = new_status
                st.success(f"Status updated for Week {week_num}!")

def display_results(
    name: str,
    target_role: str, 
    profile_analysis: Dict,
    role_requirements: Dict,
    gap_analysis: Dict,
    roadmap: Dict
) -> None:
    # Store results in session state to persist across reloads
    st.session_state.profile_analysis = profile_analysis
    st.session_state.role_requirements = role_requirements
    st.session_state.gap_analysis = gap_analysis
    st.session_state.roadmap = roadmap
    
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
        display_roadmap_with_progress(roadmap)
        
        if roadmap:
            st.download_button(
                label="Download Roadmap (JSON)",
                data=json.dumps(roadmap, indent=2),
                file_name=f"{name}_{target_role.replace(' ', '_')}_roadmap.json",
                mime="application/json"
            )

def main():
    setup_ui()
    show_header()
    
    # Initialize planner
    planner = CareerRoadmapPlanner()
    
    # Check if we have existing results in session state
    if 'profile_analysis' not in st.session_state:
        st.session_state.profile_analysis = None
    if 'role_requirements' not in st.session_state:
        st.session_state.role_requirements = None
    if 'gap_analysis' not in st.session_state:
        st.session_state.gap_analysis = None
    if 'roadmap' not in st.session_state:
        st.session_state.roadmap = None
    
    # Input section
    name, resume_text, target_role = resume_input_section(planner)
    
    # Generate button - only show if we don't have results
    if st.button("Generate Career Roadmap", type="primary") and resume_text:
        with st.spinner("Analyzing your profile and creating roadmap..."):
            try:
                # Step 1: Analyze resume
                profile_analysis = planner.analyze_resume(resume_text)
                
                # Step 2: Get role requirements using RAG
                role_requirements = planner.get_role_requirements(target_role)
                
                # Step 3: Perform gap analysis
                gap_analysis = planner.analyze_gaps(
                    profile_analysis,
                    role_requirements,
                    target_role
                )
                
                # Step 4: Build personalized roadmap
                roadmap = planner.build_roadmap(
                    name,
                    target_role,
                    profile_analysis,
                    gap_analysis
                )
                
                # Display all results
                display_results(
                    name,
                    target_role, 
                    profile_analysis,
                    role_requirements,
                    gap_analysis,
                    roadmap
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Display existing results if available
    elif (st.session_state.roadmap and 
          st.session_state.profile_analysis and
          st.session_state.role_requirements and
          st.session_state.gap_analysis):
        display_results(
            name or "User",
            target_role or st.session_state.roadmap.get("target_role", "Target Role"),
            st.session_state.profile_analysis,
            st.session_state.role_requirements,
            st.session_state.gap_analysis,
            st.session_state.roadmap
        )
    
    elif not resume_text:
        st.warning("Please upload your resume to proceed")

if __name__ == "__main__":
    main()