import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def scan_jobs_task(self, keywords: list, location: str):
    """
    Celery task: logs a scan request.
    Actual Playwright automation runs via: python automation/main.py
    (Playwright must run in the main thread, not in a Celery worker)
    """
    logger.info(f"[TASK] Job scan queued | keywords={keywords} | location={location}")
    try:
        return {'status': 'queued', 'keywords': keywords, 'location': location}
    except Exception as exc:
        logger.error(f"[TASK] Scan failed: {exc}")
        raise self.retry(exc=exc, countdown=60)