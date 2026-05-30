from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'user', 'status', 'applied_at', 'created_at']
    list_filter = ['status']
    search_fields = ['job__title', 'job__company']
    readonly_fields = ['answers_log', 'error_log', 'applied_at', 'created_at', 'updated_at']