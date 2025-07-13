from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.decorators.cache import never_cache
from django.conf import settings
from .utils import send_password_reset_email

from .models import UserProfile, UserSession
from .forms import (
    UserProfileForm, UserPasswordChangeForm,
    AdminUserCreationForm, AdminUserUpdateForm, UserSearchForm, PasswordResetRequestForm
)
from .utils import get_client_ip, get_user_statistics, send_account_setup_email, is_admin_role_user

try:
    from apps.projects.models import Project
except ImportError:
    Project = None

def is_staff_user(user):
    """Test function for user_passes_test decorator."""
    return user.is_authenticated and user.is_staff

# --- Authentication Views ---

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            UserSession.objects.get_or_create(
                user=user,
                session_key=request.session.session_key,
                defaults={
                    'ip_address': get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
            
            next_page = request.GET.get('next', 'core:dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'admin_email': getattr(settings, 'ADMIN_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', 'contact-cenergi@gmail.com')),
    }
    return render(request, 'accounts/login.html', context)

@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:dashboard')

# --- Profile Management ---

@login_required
def profile_view(request):
    """User profile view and edit"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    # Get recent projects for the user
    recent_projects = []
    if Project:
        recent_projects = Project.objects.filter(
            submitted_by=request.user
        ).select_related('submitted_by').order_by('-date_created')[:5]
    
    context = {
        'form': form,
        'profile': profile,
        'stats': get_user_statistics(request.user),
        'recent_projects': recent_projects,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
    else:
        form = UserPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@never_cache
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.get(username=username)
            
            # Generate a temporary password
            temp_password = User.objects.make_random_password(length=10)
            user.set_password(temp_password)
            user.save()

            send_password_reset_email(user, temp_password)

            messages.success(request, 'A temporary password has been sent to your email address.')
            return redirect('accounts:login')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})

# --- Admin Views ---

@user_passes_test(is_admin_role_user)
def admin_users_list(request):
    """Admin view to list all users with search and filtering. Restricted to 'Admin' role."""
    users = User.objects.select_related('profile', 'profile__role').all()
    form = UserSearchForm(request.GET)

    if form.is_valid():
        search_query = form.cleaned_data.get('search')
        role = form.cleaned_data.get('role')
        status = form.cleaned_data.get('status')

        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        if role:
            users = users.filter(profile__role=role)
        if status == 'active':
            users = users.filter(is_active=True)
        elif status == 'inactive':
            users = users.filter(is_active=False)
        elif status == 'staff':
            users = users.filter(is_staff=True)

    order_by = request.GET.get('order_by', '-date_joined')
    users = users.order_by(order_by)
    
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_form': form,
        'current_order': order_by
    }
    return render(request, 'accounts/admin_users_list.html', context)

@user_passes_test(is_staff_user)
def admin_create_user_view(request):
    """Admin-only view to create a new user and send a password setup email."""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            send_account_setup_email(user, token, uid)
            
            messages.success(request, f'Successfully created user {user.username}. A password setup email has been sent.')
            return redirect('accounts:admin_users_list') 
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'accounts/admin_create_user.html', {'form': form})


@user_passes_test(is_staff_user)
def admin_user_detail(request, user_id):
    """Admin view to see user details"""
    user = get_object_or_404(User.objects.select_related('profile', 'profile__role'), pk=user_id)
    context = {
        'user_detail': user, 
        'profile': user.profile,
        'stats': get_user_statistics(user),
        'recent_sessions': UserSession.objects.filter(user=user).order_by('-created_at')[:10],
    }
    return render(request, 'accounts/admin_user_detail.html', context)

@user_passes_test(is_staff_user)
def admin_user_edit(request, user_id):
    """Admin view to edit a user."""
    user = get_object_or_404(User.objects.select_related('profile', 'profile__role'), pk=user_id)
    
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('accounts:admin_user_detail', user_id=user.id)
    else:
        form = AdminUserUpdateForm(instance=user)
        
    context = {
        'form': form,
        'user_detail': user,
    }
    return render(request, 'accounts/admin_user_edit.html', context)

@user_passes_test(is_staff_user)
def admin_user_sessions(request, user_id):
    """Admin view to list all of a user's login sessions."""
    user = get_object_or_404(User.objects.select_related('profile'), pk=user_id)
    session_list = UserSession.objects.filter(user=user).order_by('-created_at')

    paginator = Paginator(session_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user_detail': user,
        'sessions': page_obj
    }
    return render(request, 'accounts/admin_user_sessions.html', context)


# --- AJAX/Action Views ---

@require_POST
@user_passes_test(is_staff_user)
def admin_user_toggle_active(request, user_id):
    """Toggles the is_active status of a user."""
    user = get_object_or_404(User.objects.select_related('profile'), pk=user_id)
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('accounts:admin_users_list')
    
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    
    messages.success(request, f'User has been {"activated" if user.is_active else "deactivated"}.')
    return redirect('accounts:admin_user_detail', user_id=user.id)

@require_POST
@user_passes_test(is_staff_user)
def admin_user_toggle_staff(request, user_id):
    """Toggles the is_staff status of a user."""
    user = get_object_or_404(User.objects.select_related('profile'), pk=user_id)
    if user == request.user:
        messages.error(request, 'You cannot change your own staff status.')
        return redirect('accounts:admin_users_list')
        
    user.is_staff = not user.is_staff
    user.save(update_fields=['is_staff'])
    
    messages.success(request, f'User staff status has been {"granted" if user.is_staff else "revoked"}.')
    return redirect('accounts:admin_users_list')

@require_POST
@user_passes_test(is_staff_user)
def admin_reset_password(request, user_id):
    """Admin-only view to reset a user's password and send a temporary password via email."""
    user = get_object_or_404(User, pk=user_id)
    
    if not user.email:
        messages.error(request, f'User {user.username} does not have an email address configured. Cannot send temporary password.')
        return redirect('accounts:admin_users_list')

    try:
        temp_password = User.objects.make_random_password(length=10)
        user.set_password(temp_password)
        user.save()

        send_password_reset_email(user, temp_password)

        messages.success(request, f'A temporary password has been sent to {user.email} for user {user.username}.')
    except Exception as e:
        messages.error(request, f'Failed to reset password for {user.username}: {str(e)}')
    
    return redirect('accounts:admin_users_list')

# --- ADD THIS MISSING API VIEW ---
@login_required
def dashboard_stats_api(request):
    """API endpoint to provide statistics for the admin dashboard."""
    stats = {
        'users': {
            'total': User.objects.count(),
            'active': User.objects.filter(is_active=True).count(),
            'staff': User.objects.filter(is_staff=True).count(),
        },
        'sessions': {
            'active_now': UserSession.objects.filter(is_active=True).count(),
        },
        'projects': {
            'total': 0,
            'pending': 0,
            'approved': 0,
            'rejected': 0,
        }
    }

    if Project:
        stats['projects'] = {
            'total': Project.objects.count(),
            'pending': Project.objects.filter(status='Pending_Approval').count(),
            'approved': Project.objects.filter(status='Approved').count(),
            'rejected': Project.objects.filter(status='Rejected').count(),
        }

    return JsonResponse(stats)


