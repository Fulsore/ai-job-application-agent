from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.get_profile, name='user-profile'),
    path('profile/update/', views.update_profile, name='user-profile-update'),
]