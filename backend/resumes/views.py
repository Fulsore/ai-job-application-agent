import os
import sys
import logging
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Resume
from .serializers import ResumeSerializer, ResumeUploadSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_resumes(request):
    resumes = Resume.objects.filter(user=request.user)
    serializer = ResumeSerializer(resumes, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_resume(request):
    serializer = ResumeUploadSerializer(data=request.data)
    if serializer.is_valid():
        resume = serializer.save(user=request.user)
        _parse_resume_async(resume)
        return Response(
            ResumeSerializer(resume, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_resume(request, pk):
    try:
        resume = Resume.objects.get(pk=pk, user=request.user)
        resume.file.delete(save=False)
        resume.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Resume.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


def _parse_resume_async(resume: Resume):
    """Parse uploaded resume using automation layer."""
    try:
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from automation.ai.resume_parser import ResumeParser

        parser = ResumeParser()
        data = parser.parse(resume.file.path)

        resume.parsed_text = data.get('raw_text', '')
        resume.extracted_skills = data.get('skills', [])
        resume.extracted_name = data.get('full_name', '')
        resume.extracted_email = data.get('email', '')
        resume.extracted_phone = data.get('phone', '')
        resume.save(update_fields=[
            'parsed_text', 'extracted_skills', 'extracted_name',
            'extracted_email', 'extracted_phone',
        ])
    except Exception as e:
        logger.error(f"Resume parsing failed for id={resume.pk}: {e}")