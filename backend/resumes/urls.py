from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_resumes, name='resume-list'),
    path('upload/', views.upload_resume, name='resume-upload'),
    path('<int:pk>/', views.delete_resume, name='resume-delete'),
]