from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location', 'salary', 'description',
            'link', 'platform', 'platform_job_id', 'is_easy_apply',
        ]