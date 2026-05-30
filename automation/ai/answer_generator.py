"""
Generates professional answers for job application questions.
Uses quick rules for common patterns, falls back to Groq AI.
"""

from automation.ai.groq_client import call_groq
from automation.utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM = """You fill out job application forms on behalf of a candidate.
Rules:
- Keep answers SHORT and PROFESSIONAL (1-3 sentences max, unless it is a cover letter)
- Use only information from the resume data provided
- Do NOT invent specific numbers, company names, or dates
- For yes/no questions: respond ONLY with "Yes" or "No"
- For notice period: default to "30 days" if not stated
- For salary: respond "Negotiable" if no data is available
- For sponsorship/work authorization: respond "Yes, I am authorized to work"
"""


class AnswerGenerator:
    """Generate answers for job application form fields using rules + AI."""

    def generate_answer(self, question: str, resume_data: dict) -> str:
        """
        Args:
            question: The form field label text
            resume_data: Parsed resume dict from ResumeParser

        Returns:
            Answer string (never None)
        """
        quick = self._quick_rules(question, resume_data)
        if quick is not None:
            return quick

        return self._ai_answer(question, resume_data)

    def _quick_rules(self, question: str, resume_data: dict):
        """Return a value immediately for well-known question patterns."""
        q = question.lower().strip()

        if any(w in q for w in ['sponsor', 'visa', 'work authoriz', 'eligible to work']):
            return 'Yes, I am authorized to work and do not require sponsorship'

        if 'legally' in q and 'work' in q:
            return 'Yes'

        if 'relocat' in q:
            return 'Yes'

        if 'remote' in q and 'work' in q:
            return 'Yes'

        if 'years' in q and 'experience' in q:
            return resume_data.get('years_of_experience', '3')

        if 'notice' in q:
            return resume_data.get('notice_period', '30 days')

        if any(w in q for w in ['expected salary', 'desired salary', 'ctc expected', 'compensation']):
            return resume_data.get('expected_salary', 'Negotiable')

        if 'current salary' in q or 'current ctc' in q:
            return resume_data.get('current_salary', 'Negotiable')

        return None  # Not handled by quick rules

    def _ai_answer(self, question: str, resume_data: dict) -> str:
        """Use Groq LLM to answer the question."""
        skills_str = ', '.join(resume_data.get('skills', [])[:8])
        prompt = f"""Candidate Resume Summary:
- Name: {resume_data.get('full_name', 'Candidate')}
- Email: {resume_data.get('email', '')}
- Skills: {skills_str}
- Experience: {resume_data.get('years_of_experience', 'N/A')} years
- Location: {resume_data.get('city', '')}

Application Form Question:
"{question}"

Provide a concise, professional answer:"""

        answer = call_groq(prompt, system=_SYSTEM, max_tokens=250)
        if answer:
            logger.info(f"AI answered '{question[:60]}' → '{answer[:80]}'")
        return answer