from rest_framework import serializers
from .models import Application
from jobs.serializers import JobSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    job_detail = JobSerializer(source='job', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'job_detail', 'resume', 'status', 'notes',
            'answers_log', 'error_log', 'applied_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'answers_log', 'error_log', 'applied_at', 'created_at', 'updated_at']