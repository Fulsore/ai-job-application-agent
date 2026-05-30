from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'linkedin_profile',
            'target_role', 'target_location', 'min_salary',
            'years_of_experience', 'notice_period_days',
            'requires_sponsorship', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'phone', 'linkedin_profile', 'target_role', 'target_location',
            'min_salary', 'years_of_experience', 'notice_period_days',
            'requires_sponsorship',
        ]