import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (one level above automation/)
_root = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_root / '.env')


class Config:
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
    OPENROUTER_API_KEY: str = os.getenv('OPENROUTER_API_KEY', '')
    CHROME_CDP_URL: str = os.getenv('CHROME_CDP_URL', 'http://127.0.0.1:9222')
    DEFAULT_RESUME_PATH: str = os.getenv('DEFAULT_RESUME_PATH', 'resumes/resume.pdf')
    MAX_APPLICATIONS: int = int(os.getenv('MAX_APPLICATIONS_PER_SESSION', '30'))
    HUMAN_APPROVAL_REQUIRED: bool = os.getenv('HUMAN_APPROVAL_REQUIRED', 'True') == 'True'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')


config = Config()