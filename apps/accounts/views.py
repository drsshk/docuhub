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


# --- DRF API Views ---
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .models import Role
from .serializers import UserProfileSerializer, ChangePasswordSerializer
from django.contrib.auth import update_session_auth_hash

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """API endpoint for user login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password are required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        if user.is_active:
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            
            # Create user session - handle null session_key for API requests
            session_key = request.session.session_key
            if not session_key:
                # Force session creation for API requests
                request.session.create()
                session_key = request.session.session_key
            
            UserSession.objects.get_or_create(
                user=user,
                session_key=session_key,
                defaults={
                    'ip_address': get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'is_active': True,
                }
            )
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Account is disabled'}, 
                           status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Invalid credentials'}, 
                       status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def api_logout(request):
    """API endpoint for user logout"""
    try:
        # Delete the token
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        
        # Mark session as inactive
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.filter(
                user=request.user,
                session_key=session_key
            ).update(is_active=False)
        
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_user(request):
    """API endpoint to get/update current user info"""
    if request.method == 'GET':
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_staff': request.user.is_staff,
        }, status=status.HTTP_200_OK)
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    """API endpoint to change current user's password"""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        current_password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')

        if not user.check_password(current_password):
            return Response({'current_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user) # Important to keep user logged in

        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_password_reset_request(request):
    """API endpoint to request a password reset by email."""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Return a generic success message to prevent email enumeration
        return Response({'message': 'If an account with that email exists, a temporary password has been sent.'}, status=status.HTTP_200_OK)

    try:
        temp_password = User.objects.make_random_password(length=10)
        user.set_password(temp_password)
        user.save()

        # Send email with temporary password and reminder to change
        # The send_password_reset_email utility function needs to be updated
        # to accept a temporary password directly or a flag for this scenario.
        # For now, we'll assume it can handle a direct password or we'll modify it.
        # Let's modify send_password_reset_email to accept a direct password.
        send_password_reset_email(user, temp_password, is_temp_password=True)

        return Response({'message': 'If an account with that email exists, a temporary password has been sent.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to send password reset email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- User Management API Views ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_users_list(request):
    """API endpoint to list all users with filtering"""
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.select_related('profile', 'profile__role').all()
    
    # Apply filters
    search = request.GET.get('search', '')
    role_id = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(profile__employee_id__icontains=search)
        )
    
    if role_id:
        users = users.filter(profile__role_id=role_id)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'staff':
        users = users.filter(is_staff=True)
    
    # Serialize user data
    user_data = []
    for user in users:
        profile = user.profile
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'profile': {
                'department': profile.department,
                'phone_number': profile.phone_number,
                'job_title': profile.job_title,
                'employee_id': profile.employee_id,
                'bio': profile.bio,
                'location': profile.location,
                'hire_date': profile.hire_date.isoformat() if profile.hire_date else None,
                'is_active_employee': profile.is_active_employee,
                'email_notifications': profile.email_notifications,
                'sms_notifications': profile.sms_notifications,
                'role': {
                    'id': str(profile.role.id),
                    'name': profile.role.name,
                    'description': profile.role.description,
                } if profile.role else None
            }
        })
    
    return Response({'users': user_data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_roles_list(request):
    """API endpoint to list all roles"""
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    roles = Role.objects.all()
    roles_data = [{'id': str(role.id), 'name': role.name, 'description': role.description} for role in roles]
    
    return Response({'roles': roles_data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_sessions(request, user_id):
    """API endpoint to get user sessions"""
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        sessions = UserSession.objects.filter(user=user).order_by('-created_at')
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': str(session.id),
                'session_key': session.session_key,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'is_active': session.is_active
            })
        
        return Response({'sessions': sessions_data}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_user_toggle_active(request, user_id):
    """API endpoint to toggle user active status"""
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        if user == request.user:
            return Response({'error': 'Cannot change your own status'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        
        return Response({
            'message': f'User has been {"activated" if user.is_active else "deactivated"}',
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_user_toggle_staff(request, user_id):
    """API endpoint to toggle user staff status"""
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        if user == request.user:
            return Response({'error': 'Cannot change your own staff status'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_staff = not user.is_staff
        user.save(update_fields=['is_staff'])
        
        return Response({
            'message': f'User staff status has been {"granted" if user.is_staff else "revoked"}',
            'is_staff': user.is_staff
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_user_reset_password(request, user_id):
    """API endpoint to reset user password"""
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        
        if not user.email:
            return Response({'error': 'User does not have an email address'}, status=status.HTTP_400_BAD_REQUEST)
        
        temp_password = User.objects.make_random_password(length=10)
        user.set_password(temp_password)
        user.save()
        
        send_password_reset_email(user, temp_password)
        
        return Response({
            'message': f'Temporary password has been sent to {user.email}'
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Failed to reset password: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_user(request):
    """API endpoint to create a new user"""
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['username', 'email', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_staff=data.get('is_staff', False),
            is_active=data.get('is_active', True)
        )
        
        # Update profile
        profile = user.profile
        profile.department = data.get('department', '')
        profile.phone_number = data.get('phone_number', '')
        profile.job_title = data.get('job_title', '')
        profile.employee_id = data.get('employee_id', '')
        profile.bio = data.get('bio', '')
        profile.location = data.get('location', '')
        
        # Set role if provided
        role_id = data.get('role_id')
        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                profile.role = role
            except Role.DoesNotExist:
                pass
        
        profile.save()
        
        # Send account setup email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        send_account_setup_email(user, token, uid)
        
        return Response({
            'message': 'User created successfully. Account setup email sent.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'Failed to create user: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
