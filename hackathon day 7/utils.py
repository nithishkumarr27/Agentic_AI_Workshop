import re
import json
from typing import Dict, List, Optional
from PyPDF2 import PdfReader

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text content from PDF resume."""
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_skills_from_text(text: str) -> List[str]:
    """Basic skill extraction using regex patterns."""
    skill_patterns = [
        r"\b(?:Python|Java|C\+\+|JavaScript|TypeScript)\b",
        r"\b(?:Machine Learning|ML|Deep Learning|DL|Natural Language Processing|NLP)\b",
        r"\b(?:TensorFlow|PyTorch|Keras|scikit-learn)\b",
        r"\b(?:SQL|NoSQL|MongoDB|PostgreSQL|MySQL)\b",
        r"\b(?:AWS|Azure|GCP|Docker|Kubernetes)\b"
    ]
    
    found_skills = set()
    for pattern in skill_patterns:
        found_skills.update(re.findall(pattern, text, re.IGNORECASE))
    
    return list(found_skills)

def save_job_description(company_name: str, job_description: Dict):
    """Save job description to company_data folder."""
    filename = f"company_data/{company_name.lower().replace(' ', '_')}.json"
    with open(filename, 'w') as f:
        json.dump(job_description, f)