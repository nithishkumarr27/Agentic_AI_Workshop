
import streamlit as st
st.set_page_config(
    page_title="Career Accelerator AI",
    page_icon="🤖",
    layout="wide"
)
import pandas as pd
import plotly.express as px
import os
from pathlib import Path
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
load_dotenv()
from agents import (
    ProfileAnalyzerAgent,
    RoleRequirementRetrieverAgent, 
    GapAnalysisAgent,
    RoadmapBuilderAgent
)
from rag_pipeline import RAGPipeline
from utils import parse_resume_pdf, validate_gemini_key

# Set default Gemini key
default_gemini_key = os.getenv("GOOGLE_AI_API_KEY", "")

# Custom CSS for light theme
st.markdown("""
<style>
    :root {
        --primary: #4a6fa5;
        --secondary: #6b8cae;
        --accent: #3a7bd5;
        --dark: #2c3e50;
        --light: #ffffff;
        --background: #f5f7fa;
        --success: #28a745;
        --warning: #ffc107;
        --danger: #dc3545;
        --info: #17a2b8;
        --text: #333333;
        --card-bg: #ffffff;
        --border: #e0e0e0;
    }
    
    body, .stApp {
        color: var(--text) !important;
        background-color: var(--background) !important;
    }
    
    .stSidebar {
        background-color: var(--light) !important;
        border-right: 1px solid var(--border);
    }
    
    /* Sidebar text */
    .stSidebar * {
        color: var(--text) !important;
    }
    
    /* Main content text */
    .stMarkdown, .stText, .stAlert, .stExpander {
        color: var(--text) !important;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary) !important;
    }
    
    /* White text exceptions - use 'white-text' class */
    .white-text {
        color: white !important;
    }
    
    .agent-card {
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background: var(--card-bg);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border);
    }
    
    .agent-title {
        color: var(--primary);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .success-box {
        background-color: rgba(40, 167, 69, 0.1);
        border-left: 4px solid var(--success);
        padding: 15px;
        border-radius: 5px;
        color: var(--text) !important;
    }
    
    .warning-box {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 4px solid var(--warning);
        padding: 15px;
        border-radius: 5px;
        color: var(--text) !important;
    }
    
    .danger-box {
        background-color: rgba(220, 53, 69, 0.1);
        border-left: 4px solid var(--danger);
        padding: 15px;
        border-radius: 5px;
        color: var(--text) !important;
    }
    
    .info-box {
        background-color: rgba(23, 162, 184, 0.1);
        border-left: 4px solid var(--info);
        padding: 15px;
        border-radius: 5px;
        color: var(--text) !important;
    }
    
    /* Form elements */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        color: var(--text) !important;
        background-color: var(--light) !important;
        border: 1px solid var(--border) !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary) !important;
    }
    
    /* Expander */
    .stExpander {
        background-color: var(--light) !important;
        border: 1px solid var(--border) !important;
    }
    
    /* Divider */
    hr {
        border-color: var(--border) !important;
    }
    
    /* Progress bar */
    .stProgress>div>div>div {
        background-color: var(--primary) !important;
    }
</style>
""", unsafe_allow_html=True)
def initialize_session_state():
    """Initialize all session state variables"""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = None
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = None
    if 'gap_analysis' not in st.session_state:
        st.session_state.gap_analysis = None
    if 'roadmap' not in st.session_state:
        st.session_state.roadmap = None
    if 'gemini_key_valid' not in st.session_state:
        st.session_state.gemini_key_valid = False

def setup_sidebar():
    """Setup sidebar with API key and configuration"""
    with st.sidebar:
        st.markdown("<h1 style='color: var(--primary);'>⚙️ AI Agent Configuration</h1>", unsafe_allow_html=True)
        
        # API Key input
        gemini_key = st.text_input(
            "🔑 Gemini API Key",
            type="password",
            value=default_gemini_key, 
            help="Enter your Google Gemini API key"
        )
        
        if gemini_key:
            if validate_gemini_key(gemini_key):
                st.session_state.gemini_key_valid = True
                os.environ["GOOGLE_API_KEY"] = gemini_key
                st.markdown("<div class='success-box'>✅ API Key validated</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='danger-box'>❌ Invalid API Key</div>", unsafe_allow_html=True)
                st.session_state.gemini_key_valid = False
        
        st.divider()
        
        # Initialize RAG Pipeline button
        if st.session_state.gemini_key_valid:
            if st.button("🔄 Initialize AI Agents & Vector DB", help="Initialize all AI agents and refresh the knowledge base"):
                with st.spinner("Initializing AI agents..."):
                    try:
                        st.session_state.rag_pipeline = RAGPipeline()
                        st.session_state.rag_pipeline.initialize_vector_store()
                        st.markdown(
                            """
                            <div class="success-box">
                                ✅ AI Agents initialized successfully
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        st.markdown(
                            f"""
                            <div class="error-box">
                                ❌ Error initializing AI agents: {str(e)}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
def profile_analysis_section():
    """Profile Analysis Section"""
    st.markdown("<div class='agent-card'><div class='agent-title'><h2>🤖 Resume Analyzer Agent</h2></div></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF)",
            type=['pdf'],
            key="resume_upload"
        )
        
        if uploaded_file and st.button("🔍 Analyze Resume", key="analyze_resume"):
            with st.spinner("AI agent analyzing your resume..."):
                try:
                    resume_text = parse_resume_pdf(uploaded_file)
                    agent = ProfileAnalyzerAgent()
                    profile = agent.analyze_profile(resume_text)
                    st.session_state.user_profile = profile
                    st.markdown("<div class='success-box'>✅ Resume analysis complete</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"<div class='danger-box'>❌ Error analyzing resume: {str(e)}</div>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("✍️ Manual Input")
        manual_input = st.text_area(
            "Or describe your skills and experience",
            height=150,
            placeholder="e.g., Python developer with 3 years experience in Django, React, AWS..."
        )
        
        if manual_input and st.button("🔍 Analyze Profile", key="analyze_manual"):
            with st.spinner("AI agent analyzing your profile..."):
                try:
                    agent = ProfileAnalyzerAgent()
                    profile = agent.analyze_profile(manual_input)
                    st.session_state.user_profile = profile
                    st.markdown("<div class='success-box'>✅ Profile analysis complete</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"<div class='danger-box'>❌ Error analyzing profile: {str(e)}</div>", unsafe_allow_html=True)
    
    # Display current profile
    if st.session_state.user_profile:
        st.subheader("📊 Your AI-Generated Profile")
        profile = st.session_state.user_profile
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🛠️ Technical Skills:**")
            for skill in profile.get('technical_skills', []):
                st.markdown(f"<div style='padding: 5px;'>• {skill}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**🤝 Soft Skills:**")
            for skill in profile.get('soft_skills', []):
                st.markdown(f"<div style='padding: 5px;'>• {skill}</div>", unsafe_allow_html=True)

def role_selection_section():
    """Role Selection and Requirement Retrieval"""
    st.markdown("<div class='agent-card'><div class='agent-title'><h2>📑 JD Extraction Agent (RAG)</h2></div></div>", unsafe_allow_html=True)
    
    if not st.session_state.rag_pipeline:
        st.markdown("<div class='warning-box'>⚠️ Please initialize the AI Agents first from the sidebar</div>", unsafe_allow_html=True)
        return
    
    # Get available companies/roles
    available_docs = st.session_state.rag_pipeline.get_available_documents()
    
    if not available_docs:
        st.markdown("<div class='warning-box'>⚠️ No company data found. Please add job descriptions to the company_data/ folder</div>", unsafe_allow_html=True)
        return
    
    selected_doc = st.selectbox(
        "🔎 Select a company/role to analyze",
        options=available_docs,
        key="role_selection"
    )
    
    if selected_doc and st.button("🔍 Extract Role Requirements", key="analyze_role"):
        with st.spinner("AI agent extracting requirements..."):
            try:
                agent = RoleRequirementRetrieverAgent(st.session_state.rag_pipeline)
                role_requirements = agent.get_role_requirements(selected_doc)
                st.session_state.selected_role = {
                    'document': selected_doc,
                    'requirements': role_requirements
                }
                st.markdown("<div class='success-box'>✅ Role requirements extracted</div>", unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"<div class='danger-box'>❌ Error analyzing role: {str(e)}</div>", unsafe_allow_html=True)
    
    # Display role requirements
    if st.session_state.selected_role:
        st.subheader("📋 AI-Extracted Role Requirements")
        reqs = st.session_state.selected_role['requirements']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔴 Must-Have Skills:**")
            for skill in reqs.get('must_have_skills', []):
                st.markdown(f"<div style='padding: 5px;'>• {skill}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**🟡 Nice-to-Have Skills:**")
            for skill in reqs.get('nice_to_have_skills', []):
                st.markdown(f"<div style='padding: 5px;'>• {skill}</div>", unsafe_allow_html=True)

def gap_analysis_section():
    """Gap Analysis Section"""
    st.markdown("<div class='agent-card'><div class='agent-title'><h2>📊 Skill Gap Analyzer Agent</h2></div></div>", unsafe_allow_html=True)
    
    if not st.session_state.user_profile or not st.session_state.selected_role:
        st.markdown("<div class='warning-box'>⚠️ Please complete profile analysis and role selection first</div>", unsafe_allow_html=True)
        return
    
    if st.button("🔍 Analyze Skill Gaps", key="analyze_gaps"):
        with st.spinner("AI agent analyzing your skill gaps..."):
            try:
                agent = GapAnalysisAgent()
                gap_analysis = agent.analyze_gaps(
                    st.session_state.user_profile,
                    st.session_state.selected_role['requirements']
                )
                st.session_state.gap_analysis = gap_analysis
                st.markdown("<div class='success-box'>✅ Gap analysis completed</div>", unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"<div class='danger-box'>❌ Error in gap analysis: {str(e)}</div>", unsafe_allow_html=True)
    
    # Display gap analysis
    if st.session_state.gap_analysis:
        gaps = st.session_state.gap_analysis
        
        # Critical gaps
        if gaps.get('critical_gaps'):
            st.subheader("🔴 Critical Gaps (Must Address)")
            for gap in gaps['critical_gaps']:
                st.markdown(f"<div class='danger-box' style='margin-bottom: 10px;'>• {gap}</div>", unsafe_allow_html=True)
        
        # Intermediate gaps
        if gaps.get('intermediate_gaps'):
            st.subheader("🟡 Intermediate Gaps")
            for gap in gaps['intermediate_gaps']:
                st.markdown(f"<div class='warning-box' style='margin-bottom: 10px;'>• {gap}</div>", unsafe_allow_html=True)
        
        # Bonus gaps
        if gaps.get('bonus_gaps'):
            st.subheader("🟢 Bonus Skills")
            for gap in gaps['bonus_gaps']:
                st.markdown(f"<div class='info-box' style='margin-bottom: 10px;'>• {gap}</div>", unsafe_allow_html=True)
        
        # Strengths
        if gaps.get('strengths'):
            st.subheader("✅ Your Strengths")
            for strength in gaps['strengths']:
                st.markdown(f"<div class='success-box' style='margin-bottom: 10px;'>• {strength}</div>", unsafe_allow_html=True)

def roadmap_section():
    """Learning Roadmap Section"""
    st.markdown("<div class='agent-card'><div class='agent-title'><h2>🗺️ Roadmap Creator Agent</h2></div></div>", unsafe_allow_html=True)
    
    if not st.session_state.gap_analysis:
        st.markdown("<div class='warning-box'>⚠️ Please complete gap analysis first</div>", unsafe_allow_html=True)
        return
    
    if st.button("🚀 Generate Personalized Roadmap", key="generate_roadmap"):
        with st.spinner("AI agent building your learning roadmap..."):
            try:
                agent = RoadmapBuilderAgent()
                roadmap = agent.build_roadmap(
                    st.session_state.gap_analysis,
                    st.session_state.user_profile,
                    st.session_state.selected_role
                )
                # Initialize status for each milestone if not already present
                for milestone in roadmap.get('milestones', []):
                    if 'status' not in milestone:
                        milestone['status'] = 'Not Started'
                st.session_state.roadmap = roadmap
                st.markdown("<div class='success-box'>✅ AI-generated roadmap ready</div>", unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"<div class='danger-box'>❌ Error generating roadmap: {str(e)}</div>", unsafe_allow_html=True)
    
    # Display roadmap
    if st.session_state.roadmap:
        roadmap = st.session_state.roadmap
        
        # Overall timeline
        st.subheader("⏱️ AI-Suggested Timeline")
        st.markdown(f"**⏳ Estimated Duration:** {roadmap.get('total_duration', 'N/A')}")
        
        # Calculate progress statistics
        total_milestones = len(roadmap.get('milestones', []))
        completed_milestones = sum(1 for m in roadmap.get('milestones', []) if m.get('status') == 'Completed')
        in_progress_milestones = sum(1 for m in roadmap.get('milestones', []) if m.get('status') == 'In Progress')
        progress_percentage = int((completed_milestones / total_milestones * 100)) if total_milestones > 0 else 0
        
        # Visual progress bar
        st.subheader("📈 Overall Progress")
        st.progress(progress_percentage)

        # Custom CSS to change metric text color
        st.markdown("""
        <style>
        /* Total Milestones */
        div[data-testid="stMetric"]:nth-child(1) {
            color: #1f77b4;
        }
        /* Completed */
        div[data-testid="stMetric"]:nth-child(2) {
            color: #2ca02c;
        }
        /* In Progress */
        div[data-testid="stMetric"]:nth-child(3) {
            color: #ff7f0e;
        }
        </style>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Milestones", total_milestones)
        col2.metric("Completed", completed_milestones, f"{progress_percentage}%")
        col3.metric("In Progress", in_progress_milestones)
        
        # Milestones
        if roadmap.get('milestones'):
            st.subheader("🎯 Learning Milestones")
            for i, milestone in enumerate(roadmap['milestones'], 1):
                with st.expander(f"📌 Milestone {i}: {milestone.get('title', 'N/A')} - {milestone.get('status', 'Not Started')}"):
                    # Status selector
                    status = st.selectbox(
                        f"Update status for Milestone {i}",
                        options=['Not Started', 'In Progress', 'Completed'],
                        index=['Not Started', 'In Progress', 'Completed'].index(milestone.get('status', 'Not Started')),
                        key=f"milestone_status_{i}"
                    )
                    # Update status in the roadmap
                    milestone['status'] = status
                    
                    # Visual indicator based on status
                    if status == 'Completed':
                        st.markdown(f"<div style='background-color: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>✅ {status}</div>", unsafe_allow_html=True)
                    elif status == 'In Progress':
                        st.markdown(f"<div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>🔄 {status}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='background-color: #f8d7da; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>⏳ {status}</div>", unsafe_allow_html=True)
                    
                    st.markdown(f"**⏱️ Duration:** {milestone.get('duration', 'N/A')}")
                    st.markdown(f"**📝 Description:** {milestone.get('description', 'N/A')}")
                    
                    if milestone.get('tasks'):
                        st.markdown("**✅ Tasks:**")
                        for j, task in enumerate(milestone['tasks'], 1):
                            task_status = st.checkbox(
                                task,
                                value=(milestone.get('task_status', {}).get(str(j), False)),
                                key=f"task_{i}_{j}"
                            )
                            # Store task completion status
                            if 'task_status' not in milestone:
                                milestone['task_status'] = {}
                            milestone['task_status'][str(j)] = task_status
                    
                    if milestone.get('resources'):
                        st.markdown("**📚 Resources:**")
                        for resource in milestone['resources']:
                            st.markdown(f"• {resource}")
        
        # Progress tracking
        st.subheader("📊 Progress Visualization")
        if roadmap.get('milestones'):
            # Create a dataframe for visualization
            import pandas as pd
            import plotly.express as px
            
            progress_data = []
            for i, milestone in enumerate(roadmap['milestones'], 1):
                progress_data.append({
                    'Milestone': f"Milestone {i}",
                    'Title': milestone.get('title', ''),
                    'Status': milestone.get('status', 'Not Started'),
                    'Duration': milestone.get('duration', ''),
                    'Completion': 100 if milestone.get('status') == 'Completed' else 
                                  (50 if milestone.get('status') == 'In Progress' else 0)
                })
            
            df = pd.DataFrame(progress_data)
            
            # Status distribution pie chart
            st.markdown("**📊 Status Distribution**")
            fig1 = px.pie(df, names='Status', title='Milestone Status Distribution')
            st.plotly_chart(fig1, use_container_width=True)
            
            # Completion progress bar chart
            st.markdown("**📈 Completion Progress**")
            fig2 = px.bar(df, x='Milestone', y='Completion', 
                          color='Status',
                          title='Milestone Completion Progress',
                          text='Completion',
                          color_discrete_map={
                              'Completed': '#28a745',
                              'In Progress': '#ffc107',
                              'Not Started': '#dc3545'
                          })
            fig2.update_traces(texttemplate='%{y}%', textposition='outside')
            fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
            st.plotly_chart(fig2, use_container_width=True)

def main():
    """Main application"""
    # Light theme header
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%); 
                padding: 20px; 
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                margin-bottom: 30px;'>
        <h1 style='color: var(--primary); margin: 0;'>🤖 Career Accelerator AI</h1>
        <p style='color: var(--text); margin: 0;'>AI-powered career optimization with intelligent agents</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent introduction
    st.markdown("""
    <div style='background-color: var(--light); 
                padding: 15px; 
                border-radius: 10px;
                border: 1px solid var(--border);
                margin-bottom: 30px;'>
        <h3 style='color: var(--primary);'>Our AI Agents</h3>
        <p>This system utilizes specialized AI agents to optimize your career path:</p>
        <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>
            <div style='padding: 10px; background-color: var(--card-bg); border-radius: 5px; border: 1px solid var(--border);'>
                <b>🤖 Resume Analyzer</b> - Extracts and analyzes your skills from resumes
            </div>
            <div style='padding: 10px; background-color: var(--card-bg); border-radius: 5px; border: 1px solid var(--border);'>
                <b>📑 JD Extraction (RAG)</b> - Retrieves role requirements using AI search
            </div>
            <div style='padding: 10px; background-color: var(--card-bg); border-radius: 5px; border: 1px solid var(--border);'>
                <b>📊 Skill Gap Analyzer</b> - Identifies critical missing skills
            </div>
            <div style='padding: 10px; background-color: var(--card-bg); border-radius: 5px; border: 1px solid var(--border);'>
                <b>🗺️ Roadmap Creator</b> - Generates personalized learning paths
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Setup sidebar
    setup_sidebar()
    
    # Main content
    if not st.session_state.gemini_key_valid:
        st.markdown("<div class='warning-box'>⚠️ Please enter your Gemini API key in the sidebar to activate the AI agents</div>", unsafe_allow_html=True)
        st.markdown("<div class='info-box'>📝 Get your free API key from: https://ai.google.dev/</div>", unsafe_allow_html=True)
        return
    
    # Application sections
    profile_analysis_section()
    st.divider()
    
    role_selection_section()
    st.divider()
    
    gap_analysis_section()
    st.divider()
    
    roadmap_section()

if __name__ == "__main__":
    main()