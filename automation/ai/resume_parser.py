"""
Parse a PDF resume into a structured dictionary using PyMuPDF (fitz).
The dict is used by form_filler.py and answer_generator.py.
"""

import re
import datetime
import fitz  # pip package: pymupdf
from automation.utils.helpers import extract_email, extract_phone, extract_name_heuristic
from automation.utils.logger import get_logger

logger = get_logger(__name__)

# Common skills to scan for in resume text
KNOWN_SKILLS = [
    # Languages
    'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust',
    'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'bash', 'sql',
    # Frontend
    'react', 'angular', 'vue', 'html', 'css', 'tailwind', 'next.js', 'svelte',
    # Backend
    'django', 'flask', 'fastapi', 'node.js', 'express', 'spring boot', 'rails',
    # Databases
    'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'sqlite',
    'dynamodb', 'cassandra',
    # Data/ML
    'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
    'machine learning', 'deep learning', 'nlp', 'computer vision',
    # Cloud/DevOps
    'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'terraform', 'ansible',
    'jenkins', 'github actions', 'ci/cd', 'linux',
    # Tools
    'git', 'rest api', 'graphql', 'microservices', 'kafka', 'rabbitmq',
    'celery', 'airflow', 'spark',
]


class ResumeParser:
    """Parse a PDF resume into structured data for form filling."""

    def parse(self, pdf_path: str) -> dict:
        """
        Extract structured information from a resume PDF.

        Returns a dict with keys used by form_filler.py FIELD_MAP:
            full_name, first_name, last_name, email, phone, skills,
            years_of_experience, notice_period, expected_salary,
            city, linkedin_url, website, zip_code, cover_letter, raw_text
        """
        raw_text = self._extract_text(pdf_path)
        if not raw_text:
            return {}

        full_name = extract_name_heuristic(raw_text)
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        email = extract_email(raw_text)
        phone = extract_phone(raw_text)
        skills = self._extract_skills(raw_text)
        years_exp = self._estimate_years(raw_text)
        city = self._extract_city(raw_text)
        linkedin_url = self._extract_linkedin(raw_text)

        skills_preview = ', '.join(skills[:4]) if skills else 'software development'
        cover_letter = (
            f"I am excited to apply for this role. With {years_exp}+ years of "
            f"hands-on experience in {skills_preview}, I am confident in my ability "
            f"to add significant value to your team. I am a quick learner, a strong "
            f"collaborator, and consistently deliver high-quality results."
        )

        data = {
            'raw_text': raw_text,
            'full_name': full_name,
            'first_name': first_name,
            'last_name': last_name,
            'name': full_name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'years_of_experience': str(years_exp),
            'notice_period': '30 days',
            'expected_salary': '',
            'current_salary': '',
            'city': city,
            'linkedin_url': linkedin_url,
            'website': '',
            'zip_code': '',
            'cover_letter': cover_letter,
        }

        logger.info(
            f"Resume parsed | Name: {full_name} | Email: {email} | "
            f"Skills: {skills[:5]} | Exp: ~{years_exp} yrs"
        )
        return data

    def _extract_text(self, pdf_path: str) -> str:
        try:
            doc = fitz.open(pdf_path)
            text = ''.join(page.get_text() for page in doc)
            doc.close()
            return text.strip()
        except Exception as e:
            logger.error(f"PDF text extraction failed for '{pdf_path}': {e}")
            return ''

    def _extract_skills(self, text: str) -> list:
        text_lower = text.lower()
        return [s for s in KNOWN_SKILLS if s.lower() in text_lower]

    def _estimate_years(self, text: str) -> int:
        # Explicit mention: "5 years of experience"
        explicit = re.findall(
            r'(\d{1,2})\+?\s*years?\s*(of\s*)?(experience|exp)', text, re.IGNORECASE
        )
        if explicit:
            return max(int(m[0]) for m in explicit)

        # Count from date ranges in employment history
        year_ranges = re.findall(
            r'(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|present|current|now)',
            text, re.IGNORECASE
        )
        current = datetime.datetime.now().year
        total = sum(
            current - int(start) if end.lower() in ('present', 'current', 'now')
            else int(end) - int(start)
            for start, end in year_ranges
        )
        return min(total, 30)  # Cap at 30 years

    def _extract_city(self, text: str) -> str:
        # Looks for "City, State" or "City, Country"
        match = re.search(
            r'\b([A-Z][a-z]{2,}(?:\s[A-Z][a-z]+)?),\s*([A-Z]{2}|[A-Z][a-z]{3,})\b',
            text
        )
        return match.group(0) if match else ''

    def _extract_linkedin(self, text: str) -> str:
        match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
        return 'https://www.' + match.group(0) if match else ''