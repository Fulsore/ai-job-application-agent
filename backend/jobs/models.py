from django.db import models


class Job(models.Model):
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('indeed', 'Indeed'),
        ('naukri', 'Naukri'),
        ('wellfound', 'Wellfound'),
        ('glassdoor', 'Glassdoor'),
    ]

    STATUS_CHOICES = [
        ('discovered', 'Discovered'),
        ('queued', 'Queued for Apply'),
        ('skipped', 'Skipped'),
        ('applied', 'Applied'),
        ('failed', 'Failed'),
    ]

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    salary = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(max_length=2048)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='linkedin')
    platform_job_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='discovered')
    relevance_score = models.FloatField(default=0.0)
    is_easy_apply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
        ordering = ['-relevance_score', '-created_at']
        # Prevent duplicate job entries
        unique_together = [['link', 'platform']]

    def __str__(self):
        return f"{self.title} @ {self.company}"