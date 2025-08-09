from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # --- Authentication URLs ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- Profile URLs ---
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.change_password_view, name='change_password'),

    # --- Password Reset Flow ---
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    # This section is required for the "Set Password" email link to work.
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_set_confirm.html',
             success_url='/accounts/reset/done/'
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_set_complete.html'
         ),
         name='password_reset_complete'),

    # --- Admin User Management URLs ---
    path('admin/users/', views.admin_users_list, name='admin_users_list'),
    path('admin/users/create/', views.admin_create_user_view, name='admin_create_user'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_id>/sessions/', views.admin_user_sessions, name='admin_user_sessions'),

    # --- AJAX/Action URLs for Admin ---
    path('admin/users/<int:user_id>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('admin/users/<int:user_id>/toggle-staff/', views.admin_user_toggle_staff, name='admin_user_toggle_staff'),
    path('admin/users/<int:user_id>/reset-password/', views.admin_reset_password, name='admin_reset_password'),

    # --- API URLs ---
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/user/', views.api_user, name='api_user'),
    
    # --- User Management API URLs ---
    path('api/users/', views.api_users_list, name='api_users_list'),
    path('api/roles/', views.api_roles_list, name='api_roles_list'),
    path('api/users/<int:user_id>/sessions/', views.api_user_sessions, name='api_user_sessions'),
    path('api/users/<int:user_id>/toggle-active/', views.api_user_toggle_active, name='api_user_toggle_active'),
    path('api/users/<int:user_id>/toggle-staff/', views.api_user_toggle_staff, name='api_user_toggle_staff'),
    path('api/users/<int:user_id>/reset-password/', views.api_user_reset_password, name='api_user_reset_password'),
    path('api/users/create/', views.api_create_user, name='api_create_user'),
]