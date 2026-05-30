from django.db import models
from django.conf import settings
from jobs.models import Job
from resumes.models import Resume


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
        ('interview', 'Interview Scheduled'),
        ('offer', 'Offer Received'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        null=True,
        blank=True,
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    answers_log = models.JSONField(default=dict)   # {question: answer} pairs used
    error_log = models.TextField(blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.job.title} — {self.status}"