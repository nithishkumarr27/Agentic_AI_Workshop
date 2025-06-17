import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import streamlit as st
from io import BytesIO

# PDF processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    try:
        import pdfplumber
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False

# Google AI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

def validate_gemini_key(api_key: str) -> bool:
    """Validate Gemini API key"""
    if not GENAI_AVAILABLE:
        return False
    
    try:
        genai.configure(api_key=api_key)
        # Try a simple request to validate
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        return True
    except Exception as e:
        print(f"API key validation failed: {e}")
        return False

def parse_resume_pdf(uploaded_file) -> str:
    """Parse PDF resume and extract text"""
    if not PDF_AVAILABLE:
        st.error("PDF parsing libraries not available. Please install PyPDF2 or pdfplumber.")
        return ""
    
    try:
        # Read the uploaded file
        pdf_bytes = uploaded_file.read()
        pdf_file = BytesIO(pdf_bytes)
        
        text = ""
        
        # Try PyPDF2 first
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
            # Fallback to pdfplumber
            try:
                import pdfplumber
                pdf_file.seek(0)  # Reset file pointer
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                print(f"pdfplumber also failed: {e}")
                raise Exception("Could not parse PDF with available libraries")
        
        if not text.strip():
            raise Exception("No text could be extracted from the PDF")
        
        return clean_text(text)
        
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")
def save_job_description(company_name: str, job_description: Dict):
    """
    Save job description to company_data folder.
    
    Args:
        company_name: Name of the company
        job_description: Dictionary containing job description details
    """
    # Create company_data directory if it doesn't exist
    os.makedirs("company_data", exist_ok=True)
    
    # Generate a safe filename
    filename = f"company_data/{company_name.lower().replace(' ', '_')}_{hash(json.dumps(job_description))}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(job_description, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving job description: {e}")
        return False
def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove common PDF artifacts
    text = re.sub(r'\x00', '', text)  # Remove null characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    
    return text

def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """Extract skills from text using regex patterns"""
    
    # Comprehensive skill patterns
    programming_languages = [
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 
        'Rust', 'Swift', 'Kotlin', 'TypeScript', 'R', 'MATLAB', 'Scala'
    ]
    
    frameworks_libraries = [
        'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Express',
        'Laravel', 'Rails', 'Node.js', 'jQuery', 'Bootstrap', 'TensorFlow',
        'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn'
    ]
    
    databases = [
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'SQLite', 'Oracle', 'SQL Server', 'Cassandra', 'DynamoDB'
    ]
    
    cloud_devops = [
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
        'Git', 'Linux', 'Terraform', 'Ansible', 'CI/CD'
    ]
    
    soft_skills = [
        'leadership', 'communication', 'teamwork', 'problem solving',
        'project management', 'agile', 'scrum', 'analytical thinking',
        'creativity', 'time management', 'collaboration'
    ]
    
    # Extract skills
    found_technical = []
    found_soft = []
    
    text_lower = text.lower()
    
    # Check for programming languages
    for skill in programming_languages + frameworks_libraries + databases + cloud_devops:
        if skill.lower() in text_lower:
            found_technical.append(skill)
    
    # Check for soft skills
    for skill in soft_skills:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_soft.append(skill.title())
    
    return {
        'technical_skills': list(set(found_technical)),
        'soft_skills': list(set(found_soft))
    }

def create_company_data_folder():
    """Create company_data folder if it doesn't exist"""
    company_data_path = Path("company_data")
    company_data_path.mkdir(exist_ok=True)
    
    # Create sample job descriptions if folder is empty
    if not any(company_data_path.iterdir()):
        create_sample_job_descriptions(company_data_path)
    
    return company_data_path

def create_sample_job_descriptions(folder_path: Path):
    """Create sample job descriptions for demonstration"""
    
    sample_jobs = {
        "senior_python_developer.txt": """
Senior Python Developer - TechCorp

We are seeking a Senior Python Developer to join our growing engineering team.

Required Skills:
- 5+ years of Python development experience
- Strong experience with Django or Flask frameworks
- Proficiency in SQL and database design (PostgreSQL, MySQL)
- Experience with REST API development
- Knowledge of Git version control
- Understanding of software testing principles
- Experience with cloud platforms (AWS, Azure, or GCP)

Preferred Skills:
- Experience with React or Vue.js for full-stack development
- Knowledge of Docker and containerization
- Experience with CI/CD pipelines
- Familiarity with microservices architecture
- Experience with data processing libraries (Pandas, NumPy)
- Knowledge of machine learning frameworks (TensorFlow, PyTorch)

Soft Skills:
- Strong problem-solving abilities
- Excellent communication skills
- Leadership and mentoring experience
- Ability to work in agile/scrum environments
- Project management skills

Responsibilities:
- Design and develop scalable web applications
- Mentor junior developers
- Collaborate with cross-functional teams
- Lead technical architecture decisions
- Implement best practices for code quality and testing
        """,
        
#         "data_scientist.txt": """
# Data Scientist - DataTech Solutions

# Join our data science team to drive insights and build predictive models.

# Required Skills:
# - 3+ years of experience in data science or analytics
# - Strong proficiency in Python and R
# - Experience with machine learning algorithms and statistical analysis
# - Knowledge of SQL and database querying
# - Experience with data visualization tools (Matplotlib, Seaborn, Plotly)
# - Proficiency with pandas, NumPy, and scikit-learn
# - Understanding of statistical concepts and hypothesis testing

# Preferred Skills:
# - Experience with deep learning frameworks (TensorFlow, PyTorch, Keras)
# - Knowledge of big data technologies (Spark, Hadoop)
# - Cloud platform experience (AWS SageMaker, Azure ML, GCP AI Platform)
# - Experience with MLOps and model deployment
# - Knowledge of A/B testing and experimental design
# - Familiarity with Docker and Kubernetes

# Soft Skills:
# - Strong analytical and critical thinking
# - Excellent communication skills for presenting findings
# - Ability to translate business problems into technical solutions
# - Collaborative mindset for cross-functional work
# - Attention to detail and data quality

# Responsibilities:
# - Build and deploy machine learning models
# - Analyze large datasets to extract business insights
# - Collaborate with engineering teams on model deployment
# - Present findings to stakeholders and leadership
# - Stay current with latest ML/AI developments
#         """,
        
        "frontend_developer.txt": """
Frontend Developer - WebSolutions Inc

We're looking for a creative Frontend Developer to build amazing user experiences.

Required Skills:
- 3+ years of frontend development experience
- Expert knowledge of HTML5, CSS3, and JavaScript (ES6+)
- Strong experience with React.js or Angular
- Proficiency with responsive web design and CSS frameworks
- Experience with Git version control
- Understanding of RESTful APIs and AJAX
- Knowledge of build tools (Webpack, npm, yarn)

Preferred Skills:
- Experience with TypeScript
- Knowledge of state management (Redux, MobX, Vuex)
- Familiarity with testing frameworks (Jest, Cypress, Selenium)
- Experience with CSS preprocessors (Sass, Less)
- Understanding of SEO principles and web accessibility
- Knowledge of Progressive Web Apps (PWAs)
- Experience with design tools (Figma, Adobe XD)

Soft Skills:
- Strong attention to detail and design sense
- Good communication skills for working with designers and backend developers
- Problem-solving abilities
- Ability to work in fast-paced environments
- Customer-focused mindset

Responsibilities:
- Develop responsive and interactive web applications
- Collaborate with UX/UI designers to implement designs
- Optimize applications for maximum speed and scalability
- Ensure cross-browser compatibility
- Write clean, maintainable code
- Participate in code reviews and team discussions
        """
    }
    
    for filename, content in sample_jobs.items():
        file_path = folder_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())

def get_available_job_files(folder_path: Path = None) -> List[str]:
    """Get list of available job description files"""
    if folder_path is None:
        folder_path = Path("company_data")
    
    if not folder_path.exists():
        return []
    
    # Get all text and JSON files
    job_files = []
    for file_path in folder_path.glob("*.txt"):
        job_files.append(file_path.stem.replace('_', ' ').title())
    
    for file_path in folder_path.glob("*.json"):
        job_files.append(file_path.stem.replace('_', ' ').title())
    
    return sorted(job_files)

def load_job_description(job_name: str, folder_path: Path = None) -> str:
    """Load job description content by name"""
    if folder_path is None:
        folder_path = Path("company_data")
    
    # Convert display name back to filename
    filename = job_name.lower().replace(' ', '_')
    
    # Try .txt first, then .json
    txt_path = folder_path / f"{filename}.txt"
    json_path = folder_path / f"{filename}.json"
    
    if txt_path.exists():
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif json_path.exists():
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Assume JSON has a 'description' or 'content' field
            return data.get('description', data.get('content', str(data)))
    
    return ""

def format_skills_display(skills: List[str], max_display: int = 10) -> str:
    """Format skills list for display"""
    if not skills:
        return "None identified"
    
    if len(skills) <= max_display:
        return ", ".join(skills)
    else:
        return ", ".join(skills[:max_display]) + f" (and {len(skills) - max_display} more)"

def calculate_skill_match_percentage(user_skills: List[str], required_skills: List[str]) -> float:
    """Calculate percentage match between user skills and required skills"""
    if not required_skills:
        return 100.0
    
    user_skills_lower = [skill.lower() for skill in user_skills]
    required_skills_lower = [skill.lower() for skill in required_skills]
    
    matches = sum(1 for skill in required_skills_lower if skill in user_skills_lower)
    return (matches / len(required_skills)) * 100

def validate_file_upload(uploaded_file, allowed_types: List[str] = None) -> bool:
    """Validate uploaded file type and size"""
    if uploaded_file is None:
        return False
    
    if allowed_types:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in allowed_types:
            st.error(f"File type .{file_extension} not allowed. Allowed types: {', '.join(allowed_types)}")
            return False
    
    # Check file size (limit to 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("File size too large. Please upload a file smaller than 10MB.")
        return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip()
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename

def create_progress_bar(current: int, total: int, label: str = "Progress") -> None:
    """Create a progress bar in Streamlit"""
    if total > 0:
        progress = current / total
        st.progress(progress)
        st.text(f"{label}: {current}/{total} ({progress:.1%})")
    else:
        st.text(f"{label}: 0/0 (0%)")

def safe_json_parse(json_string: str, fallback: dict = None) -> dict:
    """Safely parse JSON string with fallback"""
    if fallback is None:
        fallback = {}
    
    try:
        import json
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return fallback

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix