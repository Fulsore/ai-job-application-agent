from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_applications, name='application-list'),
    path('stats/', views.application_stats, name='application-stats'),
    path('<int:pk>/', views.application_detail, name='application-detail'),
    path('<int:pk>/update/', views.update_application, name='application-update'),
]