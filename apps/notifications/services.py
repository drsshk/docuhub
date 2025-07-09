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
    
    def send_template_email(self, template_id: int, to_email: str, 
                          to_name: str, variables: Dict, project=None) -> bool:
        """Send email using Brevo template"""
        
        # Create email log entry
        email_log = EmailLog.objects.create(
            project=project,
            recipient_email=to_email,
            recipient_name=to_name,
            template_type=self._get_template_type(template_id),
            template_id=template_id,
            status='PENDING'
        )
        
        # If no API key is configured, mark as failed but don't crash
        if not self.api_key:
            email_log.status = 'FAILED'
            email_log.error_message = 'Brevo API key not configured'
            email_log.save()
            import logging
            logger = logging.getLogger('notifications')
            logger.warning(f"Email notification: {self._get_template_type(template_id)} to {to_email} (API not configured)")
            return False
        
        payload = {
            'sender': {
                'email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@docuhub.com'),
                'name': getattr(settings, 'BREVO_SENDER_NAME', 'DocuHub System')
            },
            'to': [{'email': to_email, 'name': to_name}],
            'templateId': template_id,
            'params': variables
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
        variables = {
            'USER_NAME': user.get_full_name() or user.username,
            'PROJECT_NAME': project.project_name,
            'PROJECT_VERSION': project.version_display,
            'SUBMISSION_DATE': project.date_submitted.strftime('%Y-%m-%d') if project.date_submitted else '',
            'PROJECT_URL': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/"
        }
        
        email_templates = getattr(settings, 'EMAIL_TEMPLATES', {})
        return self.send_template_email(
            email_templates.get('PROJECT_SUBMITTED', 1),
            user.email,
            user.get_full_name() or user.username,
            variables,
            project
        )
    
    def notify_project_approved(self, project, user, admin):
        """Send approval notification to user"""
        variables = {
            'USER_NAME': user.get_full_name() or user.username,
            'PROJECT_NAME': project.project_name,
            'PROJECT_VERSION': project.version_display,
            'REVIEW_DATE': project.date_reviewed.strftime('%Y-%m-%d') if project.date_reviewed else '',
            'REVIEWED_BY': admin.get_full_name() or admin.username,
            'PROJECT_URL': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/"
        }
        
        email_templates = getattr(settings, 'EMAIL_TEMPLATES', {})
        return self.send_template_email(
            email_templates.get('PROJECT_APPROVED', 2),
            user.email,
            user.get_full_name() or user.username,
            variables,
            project
        )
    
    def notify_project_rejected(self, project, user, admin):
        """Send rejection notification to user"""
        variables = {
            'USER_NAME': user.get_full_name() or user.username,
            'PROJECT_NAME': project.project_name,
            'PROJECT_VERSION': project.version_display,
            'REVIEW_COMMENTS': project.review_comments or '',
            'REVIEW_DATE': project.date_reviewed.strftime('%Y-%m-%d') if project.date_reviewed else '',
            'REVIEWED_BY': admin.get_full_name() or admin.username,
            'PROJECT_URL': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/"
        }
        
        email_templates = getattr(settings, 'EMAIL_TEMPLATES', {})
        return self.send_template_email(
            email_templates.get('PROJECT_REJECTED', 3),
            user.email,
            user.get_full_name() or user.username,
            variables,
            project
        )
    
    def notify_admin_new_submission(self, project, admin_users):
        """Send new submission alert to admins"""
        variables = {
            'PROJECT_NAME': project.project_name,
            'PROJECT_VERSION': project.version_display,
            'SUBMITTED_BY': project.submitted_by.get_full_name() or project.submitted_by.username,
            'SUBMISSION_DATE': project.date_submitted.strftime('%Y-%m-%d') if project.date_submitted else '',
            'PROJECT_URL': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/"
        }
        
        success_count = 0
        email_templates = getattr(settings, 'EMAIL_TEMPLATES', {})
        
        for admin in admin_users:
            variables['USER_NAME'] = admin.get_full_name() or admin.username
            if self.send_template_email(
                email_templates.get('ADMIN_NEW_SUBMISSION', 6),
                admin.email,
                admin.get_full_name() or admin.username,
                variables,
                project
            ):
                success_count += 1
        
        return success_count > 0
    
    def notify_revision_required(self, project, user, admin):
        """Send revision required notification to user"""
        variables = {
            'USER_NAME': user.get_full_name() or user.username,
            'PROJECT_NAME': project.project_name,
            'PROJECT_VERSION': project.version_display,
            'REVIEW_COMMENTS': project.review_comments or '',
            'REVIEWED_BY': admin.get_full_name() or admin.username,
            'PROJECT_URL': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/"
        }
        
        email_templates = getattr(settings, 'EMAIL_TEMPLATES', {})
        return self.send_template_email(
            email_templates.get('PROJECT_REVISE_RESUBMIT', 4),
            user.email,
            user.get_full_name() or user.username,
            variables,
            project
        )
    
    def notify_project_obsolete(self, project, user):
        """Send project obsolete notification to user"""
        variables = {
            'USER_NAME': user.get_full_name() or user.username,
            'PROJECT_NAME': project.project_name,
            'PROJECT_URL': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/projects/{project.id}/"
        }
        
        email_templates = getattr(settings, 'EMAIL_TEMPLATES', {})
        return self.send_template_email(
            email_templates.get('PROJECT_OBSOLETE', 5),
            user.email,
            user.get_full_name() or user.username,
            variables,
            project
        )

    