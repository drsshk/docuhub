from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<uuid:pk>/update/', views.ProjectUpdateView.as_view(), name='update'),
    path('<uuid:pk>/submit/', views.submit_project, name='submit'),
    path('<uuid:pk>/review/', views.review_project, name='review'),
    path('<uuid:project_pk>/add_drawing/', views.add_drawing, name='add_drawing'),
    path('drawing/<uuid:pk>/edit/', views.edit_drawing, name='edit_drawing'),
    path('drawing/<uuid:pk>/delete/', views.delete_drawing, name='delete_drawing'),
    path('admin/pending/', views.admin_pending_projects, name='admin_pending'),
    path('admin/bulk-action/', views.bulk_action_projects, name='bulk_action'),
    path('<uuid:pk>/restore/', views.restore_project, name='restore'),
    path('<uuid:pk>/recover/', views.recover_draft, name='recover_draft'),
    path('<uuid:pk>/new_version/', views.create_new_version, name='create_new_version'),
    path('history/', views.history_log, name='history_log'),
]