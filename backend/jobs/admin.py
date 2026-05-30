from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'platform', 'status', 'relevance_score', 'created_at']
    list_filter = ['platform', 'status', 'is_easy_apply']
    search_fields = ['title', 'company', 'location']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-relevance_score', '-created_at']