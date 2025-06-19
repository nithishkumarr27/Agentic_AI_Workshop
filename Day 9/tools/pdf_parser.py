import PyPDF2
from typing import Optional

def parse_resume_pdf(file_path: str) -> dict:
    """Return structured dict instead of raw text"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        
        return {
            "status": "success",
            "content": text,
            "metadata": {
                "pages": len(reader.pages),
                "source": file_path
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }