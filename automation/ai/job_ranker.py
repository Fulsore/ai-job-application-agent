"""
Ranks job listings by relevance to the candidate's resume
using TF-IDF cosine similarity (no API key required).
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from automation.utils.logger import get_logger

logger = get_logger(__name__)


class JobRanker:
    """Score job relevance and extract search keywords from resume."""

    def score_job(
        self,
        resume_text: str,
        job_description: str,
        job_title: str = '',
    ) -> float:
        """
        Compute cosine similarity between resume and job posting.

        Returns:
            Float 0.0–1.0 (higher = more relevant)
        """
        if not resume_text or not (job_description or job_title):
            return 0.0
        try:
            # Weight job title twice (prepend it)
            job_text = f"{job_title} {job_title} {job_description}"
            vect = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=5000,
            )
            matrix = vect.fit_transform([resume_text[:5000], job_text[:5000]])
            score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
            return round(float(score), 4)
        except Exception as e:
            logger.warning(f"Job scoring error: {e}")
            return 0.0

    def extract_keywords(self, resume_text: str, top_n: int = 8) -> list:
        """
        Extract the most relevant keywords from resume text for search queries.

        Returns:
            List of keyword strings
        """
        if not resume_text:
            return []
        try:
            vect = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=200,
            )
            matrix = vect.fit_transform([resume_text])
            scores = zip(vect.get_feature_names_out(), matrix.toarray()[0])
            ranked = sorted(scores, key=lambda x: x[1], reverse=True)

            # Remove pure numbers and very short tokens
            keywords = [
                w for w, _ in ranked
                if len(w) > 2 and not w.replace(' ', '').isdigit()
            ]
            return keywords[:top_n]
        except Exception as e:
            logger.warning(f"Keyword extraction error: {e}")
            return []