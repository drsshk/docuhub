from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('preferences/', views.notification_preferences, name='preferences'),
    path('email-logs/', views.email_logs, name='email_logs'),
    path('email-statistics/', views.email_statistics, name='email_statistics'),
]