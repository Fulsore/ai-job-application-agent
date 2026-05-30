from django.db import models
from django.conf import settings


class Resume(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resumes',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='resumes/')
    parsed_text = models.TextField(blank=True)
    extracted_skills = models.JSONField(default=list)
    extracted_name = models.CharField(max_length=255, blank=True)
    extracted_email = models.CharField(max_length=255, blank=True)
    extracted_phone = models.CharField(max_length=50, blank=True)
    is_default = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'resumes'
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        # Ensure only one resume is default per user
        if self.is_default and self.user_id:
            Resume.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title