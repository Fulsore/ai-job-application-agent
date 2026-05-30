from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'extracted_name', 'is_default', 'uploaded_at']
    list_filter = ['is_default']
    search_fields = ['title', 'extracted_name', 'extracted_email']
    readonly_fields = [
        'parsed_text', 'extracted_skills', 'extracted_name',
        'extracted_email', 'extracted_phone', 'uploaded_at',
    ]