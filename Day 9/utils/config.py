import os
from dotenv import load_dotenv

load_dotenv()  # Load .env or secrets.toml

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # From secrets.toml