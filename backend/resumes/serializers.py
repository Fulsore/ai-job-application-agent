from rest_framework import serializers
from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = [
            'id', 'title', 'file', 'file_url', 'parsed_text',
            'extracted_skills', 'extracted_name', 'extracted_email',
            'extracted_phone', 'is_default', 'uploaded_at',
        ]
        read_only_fields = [
            'id', 'parsed_text', 'extracted_skills',
            'extracted_name', 'extracted_email', 'extracted_phone', 'uploaded_at',
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class ResumeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['title', 'file', 'is_default']