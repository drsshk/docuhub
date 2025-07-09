from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('versions/', views.version_history, name='version_history'),
    path('versions/<int:pk>/', views.version_detail, name='version_detail'),
    path('versions/add/', views.add_version, name='add_version'),
    path('versions/<int:pk>/edit/', views.edit_version, name='edit_version'),
    path('api/current-version/', views.current_version_api, name='current_version_api'),
]