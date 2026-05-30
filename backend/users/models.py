from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    linkedin_profile = models.URLField(blank=True)
    target_role = models.CharField(max_length=255, blank=True)
    target_location = models.CharField(max_length=255, blank=True)
    min_salary = models.IntegerField(default=0)
    years_of_experience = models.IntegerField(default=0)
    notice_period_days = models.IntegerField(default=30)
    requires_sponsorship = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email or self.username