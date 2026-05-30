from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Job
from .serializers import JobSerializer
from .tasks import scan_jobs_task


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_jobs(request):
    queryset = Job.objects.all()

    platform = request.query_params.get('platform')
    job_status = request.query_params.get('status')
    if platform:
        queryset = queryset.filter(platform=platform)
    if job_status:
        queryset = queryset.filter(status=job_status)

    paginator = PageNumberPagination()
    paginator.page_size = 20
    page = paginator.paginate_queryset(queryset, request)
    return paginator.get_paginated_response(JobSerializer(page, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_detail(request, pk):
    try:
        job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(JobSerializer(job).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_job_status(request, pk):
    try:
        job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in dict(Job.STATUS_CHOICES):
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    job.status = new_status
    job.save(update_fields=['status', 'updated_at'])
    return Response(JobSerializer(job).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_job_scan(request):
    """
    Queue a background job scan via Celery.
    Body: { "keywords": ["python", "django"], "location": "Hyderabad" }
    """
    keywords = request.data.get('keywords', [])
    location = request.data.get('location', '')

    if not keywords:
        return Response(
            {'error': 'Provide at least one keyword'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    task = scan_jobs_task.delay(keywords, location)
    return Response(
        {'message': 'Scan queued', 'task_id': task.id},
        status=status.HTTP_202_ACCEPTED,
    )