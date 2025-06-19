import streamlit as st
from agents.profile_analyzer import ProfileAnalyzerAgent
from agents.role_retriever import RoleRetrieverAgent
from agents.gap_analyzer import GapAnalyzerAgent
from agents.roadmap_builder import RoadmapBuilderAgent
from utils.visualization import create_gap_radar_chart, create_roadmap_gantt_chart
import tempfile
import json
import os
from langchain.callbacks import StreamlitCallbackHandler

def analyze(self, input_data: str):
    st_callback = StreamlitCallbackHandler(st.container())
    try:
        result = self.agent.invoke(
            {"input": input_data},
            {"callbacks": [st_callback]}
        )
        return UserProfile.parse_raw(result["output"])
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        raise
# Initialize agents
@st.cache_resource
def load_agents():
    return {
        "profile_analyzer": ProfileAnalyzerAgent(),
        "role_retriever": RoleRetrieverAgent(),
        "gap_analyzer": GapAnalyzerAgent(),
        "roadmap_builder": RoadmapBuilderAgent()
    }

def main():
    st.set_page_config(
        page_title="Career Path Recommender",
        page_icon="🚀",
        layout="wide"
    )
    
    # Sidebar with theme toggle
    with st.sidebar:
        st.title("Career Path Recommender")
        st.image("https://via.placeholder.com/150", width=100)
        st.markdown("""
        **How it works:**
        1. Upload your resume or enter profile info
        2. Select your target role
        3. View skill gap analysis
        4. Get personalized learning roadmap
        """)
        
        dark_mode = st.toggle("Dark Mode", value=False)
        if dark_mode:
            st.markdown("""
            <style>
                .stApp {
                    background-color: #1a1a1a;
                    color: white;
                }
            </style>
            """, unsafe_allow_html=True)
    
    # Initialize session state
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    if "profile" not in st.session_state:
        st.session_state.profile = None
    if "role_requirements" not in st.session_state:
        st.session_state.role_requirements = None
    if "gap_analysis" not in st.session_state:
        st.session_state.gap_analysis = None
    
    # Load agents
    agents = load_agents()
    
    # Main content
    st.title("🚀 Career Path Recommender")
    st.markdown("""
    Empower your career journey with AI-powered skill gap analysis and personalized learning roadmaps.
    """)
    
    # Step 1: Profile Analysis
    if st.session_state.current_step >= 1:
        st.header("Step 1: Profile Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            upload_option = st.radio(
                "How would you like to provide your profile?",
                ("Upload Resume (PDF)", "Enter Manually")
            )
            
            if upload_option == "Upload Resume (PDF)":
                uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])
                # In your file upload section:
                if uploaded_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file.flush()
                        try:
                            profile_data = agents["profile_analyzer"].analyze(tmp_file.name)
                            st.session_state.profile = profile_data
                        except Exception as e:
                            st.error(f"Analysis failed: {str(e)}")
                        finally:
                            os.unlink(tmp_file.name)
            else:
                manual_input = st.text_area("Enter your profile information (skills, experience, etc.)")
                if manual_input and st.button("Analyze Profile"):
                    profile_data = agents["profile_analyzer"].analyze(manual_input)
                    st.session_state.profile = profile_data
        
        with col2:
            if st.session_state.profile:
                st.subheader("Your Profile Summary")
                st.json(st.session_state.profile.json())
                if st.button("Continue to Step 2"):
                    st.session_state.current_step = 2
                    st.rerun()
    
    # Step 2: Role Requirements
    if st.session_state.current_step >= 2 and st.session_state.profile:
        st.header("Step 2: Target Role Requirements")
        
        role_title = st.text_input("Enter your target role title (e.g., 'Data Scientist', 'Full Stack Developer')")
        if role_title and st.button("Get Role Requirements"):
            with st.spinner("Retrieving role requirements..."):
                role_requirements = agents["role_retriever"].retrieve_requirements(role_title)
                st.session_state.role_requirements = role_requirements
        
        if st.session_state.role_requirements:
            st.subheader(f"Requirements for {st.session_state.role_requirements.role_title}")
            st.json(st.session_state.role_requirements.json())
            
            if st.button("Continue to Step 3"):
                st.session_state.current_step = 3
                st.rerun()
    
    # Step 3: Skill Gap Analysis
    if st.session_state.current_step >= 3 and st.session_state.profile and st.session_state.role_requirements:
        st.header("Step 3: Skill Gap Analysis")
        
        if st.session_state.gap_analysis is None:
            with st.spinner("Analyzing skill gaps..."):
                gap_analysis = agents["gap_analyzer"].analyze_gaps(
                    st.session_state.profile,
                    st.session_state.role_requirements
                )
                st.session_state.gap_analysis = gap_analysis
        
        if st.session_state.gap_analysis:
            st.subheader(f"Gap Analysis for {st.session_state.gap_analysis.role_title}")
            st.plotly_chart(create_gap_radar_chart(st.session_state.gap_analysis))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Overall Match", f"{st.session_state.gap_analysis.overall_match_percentage:.0f}%")
                st.subheader("Critical Gaps")
                for gap in st.session_state.gap_analysis.critical_gaps:
                    with st.expander(f"{gap.skill} ({gap.current_level} → {gap.required_level})"):
                        st.markdown("**Resources:**")
                        for resource in gap.learning_resources:
                            st.markdown(f"- {resource}")
            
            with col2:
                st.subheader("Moderate Gaps")
                for gap in st.session_state.gap_analysis.moderate_gaps:
                    with st.expander(f"{gap.skill} ({gap.current_level} → {gap.required_level})"):
                        st.markdown("**Resources:**")
                        for resource in gap.learning_resources:
                            st.markdown(f"- {resource}")
                
                st.subheader("Covered Skills")
                st.write(", ".join([gap.skill for gap in st.session_state.gap_analysis.covered_skills]))
            
            if st.button("Continue to Step 4"):
                st.session_state.current_step = 4
                st.rerun()
    
    # Step 4: Learning Roadmap
    if st.session_state.current_step >= 4 and st.session_state.gap_analysis:
        st.header("Step 4: Personalized Learning Roadmap")
        
        if "roadmap" not in st.session_state:
            with st.spinner("Building your learning roadmap..."):
                roadmap = agents["roadmap_builder"].build_roadmap(st.session_state.gap_analysis)
                st.session_state.roadmap = roadmap
        
        if st.session_state.roadmap:
            st.subheader(f"12-Week Roadmap to {st.session_state.roadmap.role_title}")
            st.plotly_chart(create_roadmap_gantt_chart(st.session_state.roadmap))
            
            tab1, tab2 = st.tabs(["Weekly Breakdown", "Export Options"])
            
            with tab1:
                for week in st.session_state.roadmap.weeks:
                    with st.expander(f"Week {week.week_number}: {week.focus_area}"):
                        st.markdown("**Milestones:**")
                        for milestone in week.milestones:
                            st.markdown(f"- {milestone}")
                        
                        st.markdown("**Tasks:**")
                        for task in week.tasks:
                            with st.expander(task.title):
                                st.markdown(f"**Duration:** {task.duration_hours} hours")
                                st.markdown("**Description:**")
                                st.write(task.description)
                                st.markdown("**Resources:**")
                                for resource in task.resources:
                                    st.markdown(f"- {resource}")
            
            with tab2:
                st.subheader("Export Options")
                roadmap_json = st.session_state.roadmap.json()
                
                st.download_button(
                    label="Download as JSON",
                    data=roadmap_json,
                    file_name="learning_roadmap.json",
                    mime="application/json"
                )
                
                # PDF export would require additional libraries like reportlab
                st.info("PDF export coming soon!")

if __name__ == "__main__":
    main()