import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def queue_applications_task(self, job_ids: list, resume_id: int):
    """
    Mark a batch of jobs as queued for application.
    Actual Playwright automation runs separately via: python automation/main.py
    """
    logger.info(f"[TASK] Queueing {len(job_ids)} jobs for resume {resume_id}")
    try:
        from applications.models import Application
        from jobs.models import Job
        from resumes.models import Resume

        resume = Resume.objects.get(pk=resume_id)
        queued = 0

        for job_id in job_ids:
            try:
                job = Job.objects.get(pk=job_id)
                _, created = Application.objects.get_or_create(
                    job=job,
                    defaults={'resume': resume, 'status': 'pending'},
                )
                if created:
                    job.status = 'queued'
                    job.save(update_fields=['status'])
                    queued += 1
            except Job.DoesNotExist:
                logger.warning(f"Job {job_id} not found")

        return {'queued': queued}
    except Exception as exc:
        logger.error(f"[TASK] Queue failed: {exc}")
        raise self.retry(exc=exc, countdown=60)