from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Application
from .serializers import ApplicationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_applications(request):
    apps = Application.objects.filter(user=request.user)
    app_status = request.query_params.get('status')
    if app_status:
        apps = apps.filter(status=app_status)
    return Response(ApplicationSerializer(apps, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def application_detail(request, pk):
    try:
        app = Application.objects.get(pk=pk, user=request.user)
    except Application.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(ApplicationSerializer(app).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_application(request, pk):
    try:
        app = Application.objects.get(pk=pk, user=request.user)
    except Application.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    app.status = request.data.get('status', app.status)
    app.notes = request.data.get('notes', app.notes)
    app.save(update_fields=['status', 'notes', 'updated_at'])
    return Response(ApplicationSerializer(app).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def application_stats(request):
    apps = Application.objects.filter(user=request.user)
    return Response({
        'total': apps.count(),
        'pending': apps.filter(status='pending').count(),
        'submitted': apps.filter(status='submitted').count(),
        'failed': apps.filter(status='failed').count(),
        'interview': apps.filter(status='interview').count(),
        'offer': apps.filter(status='offer').count(),
    })