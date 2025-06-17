import streamlit as st
from agents import ProfileAnalyzerAgent, RoleRequirementRetrieverAgent, GapAnalysisAgent, RoadmapBuilderAgent
from rag_pipeline import RAGPipeline
from utils import extract_text_from_pdf, extract_skills_from_text, save_job_description
import json
import os
import plotly.express as px

# Initialize session state
if 'profile_data' not in st.session_state:
    st.session_state.profile_data = None
if 'requirements' not in st.session_state:
    st.session_state.requirements = None
if 'gap_analysis' not in st.session_state:
    st.session_state.gap_analysis = None
if 'roadmap' not in st.session_state:
    st.session_state.roadmap = None

# Initialize agents
rag_pipeline = RAGPipeline()
profile_analyzer = ProfileAnalyzerAgent()
requirement_retriever = RoleRequirementRetrieverAgent(rag_pipeline)
gap_analyzer = GapAnalysisAgent()
roadmap_builder = RoadmapBuilderAgent()
# Add this at the beginning of your app.py, after initializing the RAGPipeline
if not os.path.exists("faiss_index") or not os.listdir("faiss_index"):
    st.warning("FAISS index not found or empty. Creating new index...")
    rag_pipeline._create_vector_store_from_company_data()
    st.success("FAISS index created successfully!")
# UI Layout
st.title("🚀 Career AI Assistant")
st.markdown("""
Analyze your profile, identify skill gaps, and get a personalized learning roadmap to achieve your career goals faster.
""")

# Step 1: Profile Analysis
st.header("Step 1: Profile Analysis")
profile_option = st.radio("Choose input method:", ("Upload Resume (PDF)", "Enter Profile Manually"))

profile_data = None
if profile_option == "Upload Resume (PDF)":
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
    if uploaded_file and st.button("Analyze Resume"):
        with st.spinner("Analyzing your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            st.session_state.profile_data = profile_analyzer.analyze_resume(resume_text)
            st.success("Profile analysis complete!")
else:
    manual_input = st.text_area("Enter your profile information (skills, experience, education):")
    if manual_input and st.button("Analyze Profile"):
        with st.spinner("Analyzing your profile..."):
            st.session_state.profile_data = profile_analyzer.analyze_resume(manual_input)
            st.success("Profile analysis complete!")

if st.session_state.profile_data:
    st.subheader("Your Profile Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Technical Skills")
        if st.session_state.profile_data.get("technical_skills"):
            for skill in st.session_state.profile_data["technical_skills"]:
                if isinstance(skill, dict):
                    st.markdown(f"- {skill.get('skill')} ({skill.get('proficiency', '')})")
                else:
                    st.markdown(f"- {skill}")
        else:
            st.warning("No technical skills found")
    
    with col2:
        st.markdown("### Soft Skills")
        if st.session_state.profile_data.get("soft_skills"):
            for skill in st.session_state.profile_data["soft_skills"]:
                st.markdown(f"- {skill}")
        else:
            st.warning("No soft skills found")
    
    st.markdown("### Experience")
    if st.session_state.profile_data.get("experience"):
        for area, details in st.session_state.profile_data["experience"].items():
            st.markdown(f"**{area}**: {details.get('years', '')} years")
            if details.get("details"):
                st.markdown(f"*{details['details']}*")
    else:
        st.warning("No experience details found")
    
    st.markdown("### Education")
    st.write(st.session_state.profile_data.get("education", "No education information found"))
# Step 2: Role Requirements
st.header("Step 2: Target Role Requirements")
role_query = st.text_input("Enter your target role or company:")
if role_query and st.button("Get Role Requirements"):
    with st.spinner("Searching for role requirements..."):
        st.session_state.requirements = requirement_retriever.get_requirements(role_query)
        st.success(f"Found {len(st.session_state.requirements)} matching roles!")

if st.session_state.requirements:
    st.subheader("Matching Role Requirements")
    for idx, req in enumerate(st.session_state.requirements, 1):
        with st.expander(f"Role {idx}: {req['role']} at {req['company']}"):
            st.markdown(f"**Required Skills:** {req['required_skills']}")
            st.markdown(f"**Nice-to-Have Skills:** {req['nice_to_have']}")

# Step 3: Gap Analysis
if st.session_state.profile_data and st.session_state.requirements:
    st.header("Step 3: Gap Analysis")
    if st.button("Analyze Skill Gaps"):
        with st.spinner("Analyzing skill gaps..."):
            st.session_state.gap_analysis = gap_analyzer.analyze_gaps(
                st.session_state.profile_data, 
                st.session_state.requirements[0]  # Use the first matching role
            )
            st.success("Gap analysis complete!")

if st.session_state.gap_analysis:
    st.subheader("Your Skill Gap Analysis")
    
    # Visualize gaps
    gap_counts = {
        "Critical Gaps": len(st.session_state.gap_analysis.get("critical_gaps", [])),
        "Intermediate Gaps": len(st.session_state.gap_analysis.get("intermediate_gaps", [])),
        "Bonus Gaps": len(st.session_state.gap_analysis.get("bonus_gaps", []))
    }
    fig = px.bar(x=list(gap_counts.keys()), y=list(gap_counts.values()),
                 labels={'x': 'Gap Type', 'y': 'Count'},
                 title="Skill Gap Breakdown")
    st.plotly_chart(fig)
    
    for gap_type, gaps in st.session_state.gap_analysis.items():
        if gaps:
            with st.expander(f"{gap_type.replace('_', ' ').title()}"):
                for gap in gaps:
                    st.markdown(f"- {gap}")

# Step 4: Learning Roadmap
if st.session_state.gap_analysis:
    st.header("Step 4: Learning Roadmap")
    timeframe = st.select_slider("Select your preferred timeline:", 
                               options=["1 month", "3 months", "6 months", "1 year"])
    if st.button("Generate Learning Roadmap"):
        with st.spinner("Building your personalized roadmap..."):
            st.session_state.roadmap = roadmap_builder.build_roadmap(
                st.session_state.gap_analysis,
                timeframe
            )
            st.success("Roadmap generated!")

if st.session_state.roadmap:
    st.subheader("Your Learning Roadmap")
    
    if isinstance(st.session_state.roadmap, dict) and "roadmap" in st.session_state.roadmap:
        st.write(st.session_state.roadmap["roadmap"])
    else:
        for week, tasks in st.session_state.roadmap.items():
            with st.expander(f"Week {week}"):
                if isinstance(tasks, dict):
                    for task, details in tasks.items():
                        st.markdown(f"**{task}**")
                        st.write(details)
                else:
                    st.write(tasks)

# Admin section to add new job descriptions
st.sidebar.header("Admin Options")
if st.sidebar.checkbox("Add New Job Description"):
    company_name = st.sidebar.text_input("Company Name")
    role_title = st.sidebar.text_input("Role Title")
    required_skills = st.sidebar.text_area("Required Skills (comma separated)")
    nice_to_have = st.sidebar.text_area("Nice-to-Have Skills (comma separated)")
    description = st.sidebar.text_area("Job Description")
    
    if st.sidebar.button("Save Job Description"):
        if not os.path.exists("company_data"):
            os.makedirs("company_data")
            
        job_data = {
            "company": company_name,
            "role": role_title,
            "required_skills": [s.strip() for s in required_skills.split(",")],
            "nice_to_have": [s.strip() for s in nice_to_have.split(",")],
            "description": description
        }
        
        save_job_description(company_name, job_data)
        st.sidebar.success("Job description saved!")
        st.sidebar.info("Please restart the app to update the vector database.")

# Add this temporary test route to your app.py
def debug_data_loading():
    """Debug function to check data loading"""
    st.write("### Debugging Data Loading")
    
    # Check company_data directory
    st.write("Files in company_data:", os.listdir("company_data"))
    
    # Check one sample file
    if os.path.exists("company_data/sample_0.json"):
        with open("company_data/sample_0.json", "r") as f:
            try:
                content = json.load(f)
                st.write("Sample file content:", content)
                st.write("Has 'description' field:", "description" in content)
            except json.JSONDecodeError:
                st.error("File is not valid JSON")
    
    # Check FAISS index
    st.write("FAISS index exists:", os.path.exists("faiss_index"))
    if os.path.exists("faiss_index"):
        st.write("Files in FAISS index:", os.listdir("faiss_index"))
        
with st.expander("Debug Data Loading"):
    debug_data_loading()