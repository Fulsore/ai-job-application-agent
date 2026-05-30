from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_jobs, name='job-list'),
    path('<int:pk>/', views.job_detail, name='job-detail'),
    path('<int:pk>/status/', views.update_job_status, name='job-status-update'),
    path('scan/', views.trigger_job_scan, name='job-scan'),
]