import os
import json
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Gemini LLM with explicit API key
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Google API key not found. Please set GOOGLE_API_KEY in your .env file")
    st.stop()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=GOOGLE_API_KEY
)

# Sample JD dataset
SAMPLE_JD_DATA = {
    "software_engineer": {
        "title": "Software Engineer",
        "required_skills": ["Python", "Java", "SQL", "Git", "Algorithms"],
        "preferred_skills": ["AWS", "Docker", "Kubernetes", "Machine Learning"],
        "description": "We're looking for a skilled software engineer with strong programming fundamentals."
    },
    "data_scientist": {
        "title": "Data Scientist",
        "required_skills": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas"],
        "preferred_skills": ["TensorFlow", "PyTorch", "Big Data", "Data Visualization"],
        "description": "Seeking a data scientist with strong analytical skills and ML experience."
    },
    "devops_engineer": {
        "title": "DevOps Engineer",
        "required_skills": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux"],
        "preferred_skills": ["Terraform", "Ansible", "Python", "Monitoring Tools"],
        "description": "Looking for a DevOps engineer to streamline our deployment processes."
    }
}

# Save sample data to JSON file
with open("jd_data.json", "w") as f:
    json.dump(SAMPLE_JD_DATA, f)

def load_jd_data():
    try:
        with open("jd_data.json", "r") as f:
            return json.load(f)
    except:
        return SAMPLE_JD_DATA

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def parse_resume(resume_text: str) -> Dict[str, Any]:
    prompt = PromptTemplate(
        template="""
        Analyze the following resume text and extract the following information in JSON format:
        - hard_skills: List of technical skills (programming languages, tools, frameworks)
        - soft_skills: List of soft skills (communication, teamwork, etc.)
        - experience: Summary of work experience
        - education: Summary of educational background

        Resume Text:
        {resume_text}

        Return ONLY valid JSON with the specified fields.
        """,
        input_variables=["resume_text"]
    )
    
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=JsonOutputParser())
    result = chain.invoke({"resume_text": resume_text})
    return result["text"]

def parse_jd(jd_text: str) -> Dict[str, Any]:
    prompt = PromptTemplate(
        template="""
        Analyze the following job description and extract the following information in JSON format:
        - required_skills: List of mandatory skills
        - preferred_skills: List of nice-to-have skills
        - role_description: Brief summary of the role

        Job Description:
        {jd_text}

        Return ONLY valid JSON with the specified fields.
        """,
        input_variables=["jd_text"]
    )
    
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=JsonOutputParser())
    result = chain.invoke({"jd_text": jd_text})
    return result["text"]

def analyze_skill_gap(resume_skills: List[str], jd_required: List[str], jd_preferred: List[str]) -> Dict[str, Any]:
    matched_required = [skill for skill in jd_required if skill.lower() in [s.lower() for s in resume_skills]]
    missing_required = [skill for skill in jd_required if skill.lower() not in [s.lower() for s in resume_skills]]
    matched_preferred = [skill for skill in jd_preferred if skill.lower() in [s.lower() for s in resume_skills]]
    missing_preferred = [skill for skill in jd_preferred if skill.lower() not in [s.lower() for s in resume_skills]]
    
    return {
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
        "match_percentage": len(matched_required) / len(jd_required) * 100 if jd_required else 0
    }

def generate_roadmap(missing_skills: List[str], role: str, duration_weeks: int = 4, intensity: str = "moderate") -> str:
    prompt = PromptTemplate(
        template="""
        Generate a {duration_weeks}-week learning roadmap to acquire the following missing skills for a {role} position.
        The roadmap should include {intensity} weekly milestones and resources for each skill.
        For each week, provide:
        - Week number and focus area
        - Specific skills to work on
        - Learning resources (free where possible)
        - Practical exercises
        - Expected outcomes

        Missing Skills:
        {missing_skills}

        Intensity levels:
        - "light" = 3-5 hours/week
        - "moderate" = 6-10 hours/week  
        - "intensive" = 15+ hours/week

        Provide the roadmap in markdown format with clear headings for each week.
        """,
        input_variables=["missing_skills", "role", "duration_weeks", "intensity"]
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.invoke({
        "missing_skills": ", ".join(missing_skills), 
        "role": role,
        "duration_weeks": duration_weeks,
        "intensity": intensity
    })
    return result["text"]

def generate_challenges(missing_skills: List[str]) -> List[Dict[str, Any]]:
    prompt = PromptTemplate(
        template="""
        Generate 5 practical challenges to help improve the following skills.
        For each skill, provide one challenge with these details:
        - title: Short challenge title
        - description: Clear instructions
        - duration: Estimated time needed
        - resources: Helpful resources

        Skills:
        {missing_skills}

        Return ONLY a valid JSON array with the specified fields for each challenge.
        """,
        input_variables=["missing_skills"]
    )
    
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=JsonOutputParser())
    result = chain.invoke({"missing_skills": ", ".join(missing_skills)})
    return result["text"]

def create_skill_gap_visualization(skill_gap: Dict[str, Any]):
    data = {
        "Skill Type": ["Required Skills", "Required Skills", "Preferred Skills", "Preferred Skills"],
        "Category": ["Matched", "Missing", "Matched", "Missing"],
        "Count": [
            len(skill_gap["matched_required"]),
            len(skill_gap["missing_required"]),
            len(skill_gap["matched_preferred"]),
            len(skill_gap["missing_preferred"])
        ]
    }
    
    df = pd.DataFrame(data)
    fig = px.bar(df, x="Skill Type", y="Count", color="Category", 
                 title="Skill Match Analysis", barmode="group")
    return fig

def create_radar_chart(resume_skills: List[str], jd_required: List[str]):
    all_skills = list(set(resume_skills + jd_required))
    resume_presence = [1 if skill in resume_skills else 0 for skill in all_skills]
    jd_presence = [1 if skill in jd_required else 0 for skill in all_skills]
    
    fig = px.line_polar(
        r=resume_presence + jd_presence,
        theta=all_skills + all_skills,
        color=["Resume"]*len(all_skills) + ["Job Description"]*len(all_skills),
        line_close=True,
        title="Skill Coverage Radar Chart"
    )
    fig.update_traces(fill='toself')
    return fig

def display_challenge_progress(challenges):
    if 'challenge_status' not in st.session_state:
        st.session_state.challenge_status = {
            i: {'status': 'not_started', 'start_date': None, 'completion_date': None}
            for i in range(1, len(challenges)+1)
        }
    
    total = len(challenges)
    completed = sum(1 for i in st.session_state.challenge_status.values() if i['status'] == 'completed')
    in_progress = sum(1 for i in st.session_state.challenge_status.values() if i['status'] == 'in_progress')
    
    progress = completed / total
    st.progress(progress)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Challenges", total)
    with col2:
        st.metric("In Progress", in_progress)
    with col3:
        st.metric("Completed", completed, f"{progress*100:.0f}%")
    
    st.caption("🎯 Not Started | 🚧 In Progress | ✅ Completed")
    
    return completed, total

def get_status_emoji(status):
    return {
        "not_started": "🎯",
        "in_progress": "🚧",
        "completed": "✅"
    }.get(status, "🎯")

def display_challenges_with_progress(challenges):
    completed, total = display_challenge_progress(challenges)
    
    for i, challenge in enumerate(challenges, 1):
        status = st.session_state.challenge_status[i]['status']
        
        with st.expander(f"{get_status_emoji(status)} Challenge {i}: {challenge['title']}"):
            st.write(f"**Description:** {challenge['description']}")
            st.write(f"**Duration:** {challenge['duration']}")
            st.write(f"**Resources:** {challenge['resources']}")
            
            current_status = st.selectbox(
                f"Status for Challenge {i}",
                ["not_started", "in_progress", "completed"],
                index=["not_started", "in_progress", "completed"].index(status),
                key=f"challenge_status_{i}"
            )
            
            if current_status != status:
                st.session_state.challenge_status[i]['status'] = current_status
                if current_status == 'in_progress' and not st.session_state.challenge_status[i]['start_date']:
                    st.session_state.challenge_status[i]['start_date'] = datetime.now().strftime("%Y-%m-%d")
                elif current_status == 'completed':
                    st.session_state.challenge_status[i]['completion_date'] = datetime.now().strftime("%Y-%m-%d")
                st.rerun()
            
            if st.session_state.challenge_status[i]['start_date']:
                st.write(f"🕒 Started on: {st.session_state.challenge_status[i]['start_date']}")
            if st.session_state.challenge_status[i]['completion_date']:
                st.write(f"🏁 Completed on: {st.session_state.challenge_status[i]['completion_date']}")

def main():
    st.set_page_config(page_title="Resume-JD Analyzer", page_icon="📊", layout="wide")
    
    st.title("📊 Resume-JD Analyzer with Gemini Flash 1.5")
    st.write("Upload your resume and select a job description to analyze your fit and get a personalized roadmap.")
    
    jd_data = load_jd_data()
    
    with st.sidebar:
        st.header("Job Description")
        jd_option = st.radio(
            "Select JD Source:",
            ("From Dataset", "Upload Custom JD")
        )
        
        if jd_option == "From Dataset":
            selected_jd = st.selectbox(
                "Select Job Description:",
                list(jd_data.keys()),
                format_func=lambda x: jd_data[x]["title"]
            )
            jd_text = json.dumps(jd_data[selected_jd])
        else:
            uploaded_jd = st.file_uploader("Upload Job Description (TXT)", type=["txt"])
            if uploaded_jd:
                jd_text = uploaded_jd.read().decode("utf-8")
            else:
                jd_text = ""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("1. Upload Your Resume")
        uploaded_resume = st.file_uploader("Choose a PDF file", type=["pdf"])
        
        if uploaded_resume:
            with st.spinner("Extracting resume text..."):
                resume_text = extract_text_from_pdf(uploaded_resume)
                st.success("Resume extracted successfully!")
                
                with st.expander("View extracted resume text"):
                    st.text(resume_text[:1000] + "...")
                
                with st.spinner("Analyzing resume..."):
                    resume_data = parse_resume(resume_text)
                    st.session_state.resume_data = resume_data
                    
                st.success("Resume analysis complete!")
                with st.expander("View resume analysis"):
                    st.json(resume_data)
    
    with col2:
        if uploaded_resume and jd_text:
            st.header("2. Job Description Analysis")
            with st.spinner("Analyzing job description..."):
                jd_data = parse_jd(jd_text)
                st.session_state.jd_data = jd_data
                
            st.success("JD analysis complete!")
            with st.expander("View JD analysis"):
                st.json(jd_data)
    
    if uploaded_resume and jd_text and "resume_data" in st.session_state and "jd_data" in st.session_state:
        st.header("3. Skill Gap Analysis")
        
        resume_skills = st.session_state.resume_data.get("hard_skills", [])
        jd_required = st.session_state.jd_data.get("required_skills", [])
        jd_preferred = st.session_state.jd_data.get("preferred_skills", [])
        
        skill_gap = analyze_skill_gap(resume_skills, jd_required, jd_preferred)
        st.session_state.skill_gap = skill_gap
        
        match_percentage = skill_gap["match_percentage"]
        color = "green" if match_percentage >= 70 else "orange" if match_percentage >= 40 else "red"
        st.metric("Required Skills Match", f"{match_percentage:.1f}%", delta_color="off")
        st.markdown(f"<div style='background-color:{color}; height:10px; width:{match_percentage}%; border-radius:5px;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Matched Required Skills")
            if skill_gap["matched_required"]:
                for skill in skill_gap["matched_required"]:
                    st.success(f"- {skill}")
            else:
                st.warning("No required skills matched")
            
            st.subheader("⚠️ Missing Preferred Skills")
            if skill_gap["missing_preferred"]:
                for skill in skill_gap["missing_preferred"]:
                    st.info(f"- {skill}")
            else:
                st.success("All preferred skills matched!")
        
        with col2:
            st.subheader("❌ Missing Required Skills")
            if skill_gap["missing_required"]:
                for skill in skill_gap["missing_required"]:
                    st.error(f"- {skill}")
            else:
                st.success("All required skills matched!")
            
            st.subheader("👍 Matched Preferred Skills")
            if skill_gap["matched_preferred"]:
                for skill in skill_gap["matched_preferred"]:
                    st.success(f"- {skill}")
            else:
                st.warning("No preferred skills matched")
        
        st.header("4. Visualizations")
        fig1 = create_skill_gap_visualization(skill_gap)
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = create_radar_chart(resume_skills, jd_required)
        st.plotly_chart(fig2, use_container_width=True)
        
        if skill_gap["missing_required"] or skill_gap["missing_preferred"]:
            missing_skills = skill_gap["missing_required"] + skill_gap["missing_preferred"]
            role = st.session_state.jd_data.get("role_description", "the position").split()[0]
            
            st.header("5. Personalized Roadmap")
            
            col1, col2 = st.columns(2)
            with col1:
                duration_weeks = st.slider("Roadmap Duration (weeks)", 1, 12, 4)
            with col2:
                intensity = st.selectbox("Learning Intensity", 
                                       ["light", "moderate", "intensive"],
                                       index=1)
            
            if st.button("Generate Roadmap"):
                with st.spinner(f"Generating {duration_weeks}-week {intensity} roadmap..."):
                    roadmap = generate_roadmap(missing_skills, role, duration_weeks, intensity)
                    st.session_state.roadmap = roadmap
                    st.session_state.roadmap_generated = datetime.now().strftime("%Y-%m-%d")
                    st.rerun()
            
            if 'roadmap' in st.session_state:
                st.markdown(st.session_state.roadmap)
                if 'roadmap_generated' in st.session_state:
                    st.caption(f"Roadmap generated on: {st.session_state.roadmap_generated}")
            
            st.header("6. Skill-Building Challenges")
            if 'challenges' not in st.session_state:
                with st.spinner("Generating practical challenges..."):
                    challenges = generate_challenges(missing_skills)
                    st.session_state.challenges = challenges
            
            if 'challenges' in st.session_state:
                display_challenges_with_progress(st.session_state.challenges)
        else:
            st.success("🎉 Congratulations! Your skills perfectly match the job requirements.")

if __name__ == "__main__":
    main()