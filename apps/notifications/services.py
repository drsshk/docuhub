import requests
import json
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone
from typing import Dict, List, Optional
from .models import EmailLog

class BrevoEmailService:
    def __init__(self):
        self.api_key = getattr(settings, 'BREVO_API_KEY', '')
        self.api_url = getattr(settings, 'BREVO_API_URL', 'https://api.brevo.com/v3/smtp/email')
        self.headers = {
            'accept': 'application/json',
            'api-key': self.api_key,
            'content-type': 'application/json'
        }
    
    def send_custom_email(self, template_name: str, to_email: str, 
                         to_name: str, subject: str, context: Dict, project=None) -> bool:
        """Send email using custom HTML template"""
        
        # Create email log entry
        email_log = EmailLog.objects.create(
            project=project,
            recipient_email=to_email,
            recipient_name=to_name,
            template_type=template_name,
            template_id=0,  # Not using Brevo template IDs
            status='PENDING'
        )
        
        # If no API key is configured, mark as failed but don't crash
        if not self.api_key:
            email_log.status = 'FAILED'
            email_log.error_message = 'Brevo API key not configured'
            email_log.save()
            import logging
            logger = logging.getLogger('notifications')
            logger.warning(f"Email notification: {template_name} to {to_email} (API not configured)")
            return False
        
        try:
            # Render custom HTML template
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = render_to_string(f'emails/{template_name}.txt', context)
        except Exception as e:
            email_log.status = 'FAILED'
            email_log.error_message = f'Template rendering failed: {str(e)}'
            email_log.save()
            import logging
            logger = logging.getLogger('notifications')
            logger.error(f"Template rendering failed: {e}")
            return False
        
        payload = {
            'sender': {
                'email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@docuhub.com'),
                'name': getattr(settings, 'BREVO_SENDER_NAME', 'DocuHub System')
            },
            'to': [{'email': to_email, 'name': to_name}],
            'subject': subject,
            'htmlContent': html_content,
            'textContent': text_content
        }
        
        try:
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 201:
                response_data = response.json()
                email_log.status = 'SENT'
                email_log.brevo_message_id = response_data.get('messageId', '')
                email_log.save()
                return True
            else:
                email_log.status = 'FAILED'
                email_log.error_message = f"HTTP {response.status_code}: {response.text}"
                email_log.save()
                return False
                
        except Exception as e:
            email_log.status = 'FAILED'
            email_log.error_message = str(e)
            email_log.save()
            import logging
            logger = logging.getLogger('notifications')
            logger.error(f"Email sending failed: {e}")
            return False
    
    def _get_template_type(self, template_id: int) -> str:
        """Get template type based on template ID"""
        email_templates = getattr(settings, 'EMAIL_TEMPLATES', {})
        template_map = {
            email_templates.get('PROJECT_SUBMITTED', 1): 'PROJECT_SUBMITTED',
            email_templates.get('PROJECT_APPROVED', 2): 'PROJECT_APPROVED',
            email_templates.get('PROJECT_REJECTED', 3): 'PROJECT_REJECTED',
            email_templates.get('PROJECT_REVISE_RESUBMIT', 4): 'PROJECT_REVISE_RESUBMIT',
            email_templates.get('PROJECT_OBSOLETE', 5): 'PROJECT_OBSOLETE',
            email_templates.get('ADMIN_NEW_SUBMISSION', 6): 'ADMIN_NEW_SUBMISSION',
            email_templates.get('ADMIN_RESUBMISSION', 7): 'ADMIN_RESUBMISSION',
            email_templates.get('PASSWORD_RESET', 8): 'PASSWORD_RESET',
        }
        return template_map.get(template_id, 'UNKNOWN')
    
    def notify_project_submitted(self, project, user):
        """Send submission confirmation to user"""
        context = {
            'user_name': user.get_full_name() or user.username,
            'project_name': project.project_name,
            'project_version': project.version_display,
            'submission_date': project.date_submitted.strftime('%B %d, %Y') if project.date_submitted else '',
            'project_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/",
            'project': project,
            'user': user
        }
        
        subject = f"Project Submitted: {project.project_name} {project.version_display}"
        
        return self.send_custom_email(
            'project_submitted',
            user.email,
            user.get_full_name() or user.username,
            subject,
            context,
            project
        )
    
    def notify_project_approved(self, project, user, admin):
        """Send approval notification to user"""
        context = {
            'user_name': user.get_full_name() or user.username,
            'project_name': project.project_name,
            'project_version': project.version_display,
            'review_date': project.date_reviewed.strftime('%B %d, %Y') if project.date_reviewed else '',
            'reviewed_by': admin.get_full_name() or admin.username,
            'project_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/",
            'project': project,
            'user': user,
            'admin': admin
        }
        
        subject = f"Project Approved: {project.project_name} {project.version_display}"
        
        return self.send_custom_email(
            'project_approved',
            user.email,
            user.get_full_name() or user.username,
            subject,
            context,
            project
        )
    
    def notify_project_rejected(self, project, user, admin):
        """Send rejection notification to user"""
        context = {
            'user_name': user.get_full_name() or user.username,
            'project_name': project.project_name,
            'project_version': project.version_display,
            'review_comments': project.review_comments or '',
            'review_date': project.date_reviewed.strftime('%B %d, %Y') if project.date_reviewed else '',
            'reviewed_by': admin.get_full_name() or admin.username,
            'project_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/",
            'project': project,
            'user': user,
            'admin': admin
        }
        
        subject = f"Project Rejected: {project.project_name} {project.version_display}"
        
        return self.send_custom_email(
            'project_rejected',
            user.email,
            user.get_full_name() or user.username,
            subject,
            context,
            project
        )
    
    def notify_admin_new_submission(self, project, admin_users):
        """Send new submission alert to admins"""
        context = {
            'project_name': project.project_name,
            'project_version': project.version_display,
            'submitted_by': project.submitted_by.get_full_name() or project.submitted_by.username,
            'submission_date': project.date_submitted.strftime('%B %d, %Y') if project.date_submitted else '',
            'project_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/",
            'project': project
        }
        
        subject = f"New Project Submission: {project.project_name} {project.version_display}"
        success_count = 0
        
        for admin in admin_users:
            admin_context = context.copy()
            admin_context['user_name'] = admin.get_full_name() or admin.username
            admin_context['admin'] = admin
            
            if self.send_custom_email(
                'admin_new_submission',
                admin.email,
                admin.get_full_name() or admin.username,
                subject,
                admin_context,
                project
            ):
                success_count += 1
        
        return success_count > 0
    
    def notify_revision_required(self, project, user, admin):
        """Send revision required notification to user"""
        context = {
            'user_name': user.get_full_name() or user.username,
            'project_name': project.project_name,
            'project_version': project.version_display,
            'review_comments': project.review_comments or '',
            'reviewed_by': admin.get_full_name() or admin.username,
            'project_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/",
            'project': project,
            'user': user,
            'admin': admin
        }
        
        subject = f"Revision Required: {project.project_name} {project.version_display}"
        
        return self.send_custom_email(
            'revision_required',
            user.email,
            user.get_full_name() or user.username,
            subject,
            context,
            project
        )
    
    def notify_project_obsolete(self, project, user):
        """Send project obsolete notification to user"""
        context = {
            'user_name': user.get_full_name() or user.username,
            'project_name': project.project_name,
            'project_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/",
            'project': project,
            'user': user
        }
        
        subject = f"Project Obsolete: {project.project_name}"
        
        return self.send_custom_email(
            'project_obsolete',
            user.email,
            user.get_full_name() or user.username,
            subject,
            context,
            project
        )
    
    def send_account_setup_email(self, user, setup_url):
        """Send account setup email to new user"""
        context = {
            'user_name': user.get_full_name() or user.username,
            'user': user,
            'reset_url': setup_url,
            'email_company_name': getattr(settings, 'EMAIL_COMPANY_NAME', 'DocuHub'),
            'email_logo_url': getattr(settings, 'EMAIL_LOGO_URL', None),
            'email_welcome_message': getattr(settings, 'EMAIL_WELCOME_MESSAGE', 'Your account has been created. Please click the link below to set your password and activate your account.'),
        }
        
        subject = f"Welcome to {context['email_company_name']} - Set Up Your Account"
        
        return self.send_custom_email(
            'new_user_welcome',
            user.email,
            user.get_full_name() or user.username,
            subject,
            context
        )
    
    def send_password_reset_email(self, user, temp_password, login_url):
        """Send password reset email with temporary password"""
        context = {
            'user_name': user.get_full_name() or user.username,
            'user': user,
            'temp_password': temp_password,
            'login_url': login_url
        }
        
        subject = f"DocuHub Password Reset"
        
        return self.send_custom_email(
            'password_reset',
            user.email,
            user.get_full_name() or user.username,
            subject,
            context
        )

    