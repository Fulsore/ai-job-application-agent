from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'target_role', 'years_of_experience', 'created_at']
    fieldsets = UserAdmin.fieldsets + (
        ('Job Preferences', {
            'fields': (
                'phone', 'linkedin_profile', 'target_role', 'target_location',
                'min_salary', 'years_of_experience', 'notice_period_days',
                'requires_sponsorship',
            )
        }),
    )