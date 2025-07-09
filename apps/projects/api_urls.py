from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'projects', api_views.ProjectViewSet, basename='project')
router.register(r'drawings', api_views.DrawingViewSet, basename='drawing')

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<uuid:pk>/submit/', api_views.submit_project_api, name='submit-project'),
    path('projects/<uuid:pk>/review/', api_views.review_project_api, name='review-project'),
]