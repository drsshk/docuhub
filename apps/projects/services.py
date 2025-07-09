"""
Business logic services for project management
"""
import logging
import uuid
from typing import Optional, Dict, Any
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Project, Drawing, ApprovalHistory, ProjectHistory
from apps.notifications.services import BrevoEmailService

logger = logging.getLogger('projects')


class ProjectVersionService:
    """Service for handling project version management"""
    
    @staticmethod
    def get_next_version_number(project_group_id: str) -> int:
        """Get the next version number for a project group"""
        latest_project = Project.objects.filter(
            project_group_id=project_group_id
        ).order_by('-version').first()
        
        return (latest_project.version + 1) if latest_project else 1
    
    @staticmethod
    def create_new_version(original_project: Project, user: User, 
                          revision_notes: str = "") -> Project:
        """Create a new version of an existing project"""
        with transaction.atomic():
            # Get next version number
            next_version = ProjectVersionService.get_next_version_number(
                original_project.project_group_id
            )
            
            # Create new project version
            new_project = Project.objects.create(
                project_group_id=original_project.project_group_id,
                project_name=original_project.project_name,
                project_description=original_project.project_description,
                version=next_version,
                submitted_by=user,
                status='Draft',
                revision_notes=revision_notes,
                client_department=original_project.client_department,
                project_priority=original_project.project_priority,
                deadline_date=original_project.deadline_date
            )
            
            # Copy drawings from original project
            original_drawings = Drawing.objects.filter(
                project=original_project,
                status='Active'
            )
            
            for drawing in original_drawings:
                Drawing.objects.create(
                    project=new_project,
                    drawing_no=drawing.drawing_no,
                    drawing_title=drawing.drawing_title,
                    drawing_description=drawing.drawing_description,
                    drawing_list_link=drawing.drawing_list_link,
                    drawing_type=drawing.drawing_type,
                    discipline=drawing.discipline,
                    scale_ratio=drawing.scale_ratio,
                    sheet_size=drawing.sheet_size,
                    revision_number=drawing.revision_number + 1,
                    added_by=user,
                    status='Active',
                    sort_order=drawing.sort_order
                )
            
            # Create approval history entry
            ApprovalHistory.objects.create(
                project=new_project,
                version=new_project.version,
                action='Version_Created',
                performed_by=user,
                comments=f"New version created from V{original_project.version:03d}. {revision_notes}",
                new_status='Draft'
            )

            # Create ProjectHistory entry for the new version
            new_drawing_numbers = ", ".join([d.drawing_no for d in new_project.drawings.all()])
            ProjectHistory.objects.create(
                project=new_project,
                version=new_project.version,
                submitted_by=user,
                date_submitted=timezone.now(),
                submission_link="",  # Placeholder
                drawing_qty=new_project.no_of_drawings,
                drawing_numbers=new_drawing_numbers,
                receipt_id="",  # Placeholder
                approval_status='Draft'
            )

            # Update the original project's ProjectHistory to Obsolete
            original_project_history = ProjectHistory.objects.filter(
                project=original_project, version=original_project.version
            ).first()
            if original_project_history:
                original_project_history.approval_status = 'Obsolete'
                original_project_history.save()
            
            # Also set the original project's status to Obsolete
            original_project.status = 'Obsolete'
            original_project.save()
            
            logger.info(
                f"New project version created: {new_project.project_name} "
                f"V{new_project.version:03d} by {user.username}"
            )
            
            return new_project


class ProjectSubmissionService:
    """Service for handling project submissions and approvals"""
    
    def __init__(self):
        self.email_service = BrevoEmailService()
    
    def submit_for_approval(self, project: Project, user: User, 
                          request_meta: Optional[Dict] = None) -> bool:
        """Submit a project for approval"""
        try:
            with transaction.atomic():
                project.status = 'Pending_Approval'
                project.date_submitted = timezone.now()
                project.save()
                
                # Create approval history entry
                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Submitted',
                    performed_by=user,
                    comments=f"Project submitted for approval",
                    previous_status='Draft',
                    new_status='Pending_Approval',
                    ip_address=request_meta.get('ip_address') if request_meta else None,
                    user_agent=request_meta.get('user_agent') if request_meta else None
                )

                # Create ProjectHistory entry
                drawing_numbers = ", ".join([d.drawing_no for d in project.drawings.all()])
                ProjectHistory.objects.create(
                    project=project,
                    version=project.version,
                    submitted_by=user,
                    date_submitted=project.date_submitted,
                    submission_link="",  # Placeholder, update if a specific link is generated
                    drawing_qty=project.no_of_drawings,
                    drawing_numbers=drawing_numbers,
                    receipt_id=str(uuid.uuid4()),  # Generate a unique receipt ID
                    approval_status='Pending_Approval'
                )
                
                # Send notification emails
                self._send_submission_notifications(project, user)
                
                logger.info(
                    f"Project submitted for approval: {project.project_name} "
                    f"V{project.version:03d} by {user.username}"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to submit project {project.id}: {e}")
            return False
    
    def approve_project(self, project: Project, admin: User, 
                       comments: str = "", request_meta: Optional[Dict] = None) -> bool:
        """Approve a project"""
        try:
            with transaction.atomic():
                project.status = 'Approved'
                project.date_reviewed = timezone.now()
                project.reviewed_by = admin
                project.review_comments = comments
                project.save()
                
                # Create approval history entry
                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Approved',
                    performed_by=admin,
                    comments=comments,
                    previous_status='Pending_Approval',
                    new_status='Approved',
                    ip_address=request_meta.get('ip_address') if request_meta else None,
                    user_agent=request_meta.get('user_agent') if request_meta else None
                )

                # Update ProjectHistory entry
                ProjectHistory.objects.filter(project=project, version=project.version).update(
                    approval_status='Approved'
                )
                
                # Send notification email
                self.email_service.notify_project_approved(
                    project, project.submitted_by, admin
                )
                
                logger.info(
                    f"Project approved: {project.project_name} "
                    f"V{project.version:03d} by {admin.username}"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to approve project {project.id}: {e}")
            return False
    
    def reject_project(self, project: Project, admin: User, 
                      comments: str = "", request_meta: Optional[Dict] = None) -> bool:
        """Reject a project"""
        try:
            with transaction.atomic():
                project.status = 'Rejected'
                project.date_reviewed = timezone.now()
                project.reviewed_by = admin
                project.review_comments = comments
                project.save()
                
                # Create approval history entry
                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Rejected',
                    performed_by=admin,
                    comments=comments,
                    previous_status='Pending_Approval',
                    new_status='Rejected',
                    ip_address=request_meta.get('ip_address') if request_meta else None,
                    user_agent=request_meta.get('user_agent') if request_meta else None
                )

                # Update ProjectHistory entry
                ProjectHistory.objects.filter(project=project, version=project.version).update(
                    approval_status='Rejected'
                )
                
                # Send notification email
                self.email_service.notify_project_rejected(
                    project, project.submitted_by, admin
                )
                
                logger.info(
                    f"Project rejected: {project.project_name} "
                    f"V{project.version:03d} by {admin.username}"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to reject project {project.id}: {e}")
            return False
    
    def request_revision(self, project: Project, admin: User, 
                        comments: str = "", request_meta: Optional[Dict] = None) -> bool:
        """Request revision for a project"""
        try:
            with transaction.atomic():
                project.status = 'Revise_and_Resubmit'
                project.date_reviewed = timezone.now()
                project.reviewed_by = admin
                project.review_comments = comments
                project.save()
                
                # Create approval history entry
                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Status_Changed',
                    performed_by=admin,
                    comments=comments,
                    previous_status='Pending_Approval',
                    new_status='Revise_and_Resubmit',
                    ip_address=request_meta.get('ip_address') if request_meta else None,
                    user_agent=request_meta.get('user_agent') if request_meta else None
                )

                # Update ProjectHistory entry
                ProjectHistory.objects.filter(project=project, version=project.version).update(
                    approval_status='Revise_and_Resubmit'
                )
                
                # Send notification email
                self.email_service.notify_revision_required(
                    project, project.submitted_by, admin
                )
                
                logger.info(
                    f"Revision requested for project: {project.project_name} "
                    f"V{project.version:03d} by {admin.username}"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to request revision for project {project.id}: {e}")
            return False
    
    def _send_submission_notifications(self, project: Project, user: User):
        """Send email notifications for project submission"""
        # Send confirmation to user
        self.email_service.notify_project_submitted(project, user)
        
        # Send notification to admins
        admin_users = User.objects.filter(is_staff=True, is_active=True).select_related('profile')
        if admin_users.exists():
            self.email_service.notify_admin_new_submission(project, admin_users)


class ProjectBulkOperationsService:
    """Service for bulk operations on projects"""
    
    def __init__(self):
        self.email_service = BrevoEmailService()
    
    @transaction.atomic
    def bulk_approve_projects(self, project_ids: list, admin: User, 
                            comments: str = "", request_meta: Optional[Dict] = None) -> Dict[str, Any]:
        """Bulk approve multiple projects"""
        results = {'success': [], 'errors': []}
        
        projects = Project.objects.filter(
            id__in=project_ids,
            status='Pending_Approval'
        )
        
        for project in projects:
            try:
                project.status = 'Approved'
                project.date_reviewed = timezone.now()
                project.reviewed_by = admin
                project.review_comments = comments
                project.save()
                
                # Create approval history entry
                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Approved',
                    performed_by=admin,
                    comments=f"Bulk approval: {comments}" if comments else "Bulk approval",
                    previous_status='Pending_Approval',
                    new_status='Approved',
                    ip_address=request_meta.get('ip_address') if request_meta else None,
                    user_agent=request_meta.get('user_agent') if request_meta else None
                )
                
                # Send notification email
                self.email_service.notify_project_approved(project, project.submitted_by, admin)
                
                results['success'].append(project.project_name)
                
            except Exception as e:
                results['errors'].append(f"{project.project_name}: {str(e)}")
                logger.error(f"Failed to bulk approve project {project.id}: {e}")
        
        return results
    
    @transaction.atomic
    def bulk_reject_projects(self, project_ids: list, admin: User, 
                           comments: str = "", request_meta: Optional[Dict] = None) -> Dict[str, Any]:
        """Bulk reject multiple projects"""
        results = {'success': [], 'errors': []}
        
        projects = Project.objects.filter(
            id__in=project_ids,
            status='Pending_Approval'
        )
        
        for project in projects:
            try:
                project.status = 'Rejected'
                project.date_reviewed = timezone.now()
                project.reviewed_by = admin
                project.review_comments = comments
                project.save()
                
                # Create approval history entry
                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Rejected',
                    performed_by=admin,
                    comments=f"Bulk rejection: {comments}" if comments else "Bulk rejection",
                    previous_status='Pending_Approval',
                    new_status='Rejected',
                    ip_address=request_meta.get('ip_address') if request_meta else None,
                    user_agent=request_meta.get('user_agent') if request_meta else None
                )
                
                # Send notification email
                self.email_service.notify_project_rejected(project, project.submitted_by, admin)
                
                results['success'].append(project.project_name)
                
            except Exception as e:
                results['errors'].append(f"{project.project_name}: {str(e)}")
                logger.error(f"Failed to bulk reject project {project.id}: {e}")
        
        return results
    
    @transaction.atomic
    def bulk_request_revision(self, project_ids: list, admin: User, 
                            comments: str = "", request_meta: Optional[Dict] = None) -> Dict[str, Any]:
        """Bulk request revision for multiple projects"""
        results = {'success': [], 'errors': []}
        
        projects = Project.objects.filter(
            id__in=project_ids,
            status='Pending_Approval'
        )
        
        for project in projects:
            try:
                project.status = 'Revise_and_Resubmit'
                project.date_reviewed = timezone.now()
                project.reviewed_by = admin
                project.review_comments = comments
                project.save()
                
                # Create approval history entry
                ApprovalHistory.objects.create(
                    project=project,
                    version=project.version,
                    action='Status_Changed',
                    performed_by=admin,
                    comments=f"Bulk revision request: {comments}" if comments else "Bulk revision request",
                    previous_status='Pending_Approval',
                    new_status='Revise_and_Resubmit',
                    ip_address=request_meta.get('ip_address') if request_meta else None,
                    user_agent=request_meta.get('user_agent') if request_meta else None
                )
                
                # Send notification email
                self.email_service.notify_revision_required(project, project.submitted_by, admin)
                
                results['success'].append(project.project_name)
                
            except Exception as e:
                results['errors'].append(f"{project.project_name}: {str(e)}")
                logger.error(f"Failed to bulk request revision for project {project.id}: {e}")
        
        return results


class ProjectRestoreService:
    """Service for restoring obsoleted projects"""
    
    @transaction.atomic
    def restore_project(self, project: Project, admin: User, 
                       restore_to_status: str, comments: str = "",
                       request_meta: Optional[Dict] = None) -> bool:
        """Restore an obsoleted project to a new status"""
        try:
            if project.status != 'Obsolete':
                raise ValueError("Only obsolete projects can be restored")
            
            old_status = project.status
            project.status = restore_to_status
            project.save()
            
            # Create approval history entry
            ApprovalHistory.objects.create(
                project=project,
                version=project.version,
                action='Status_Changed',
                performed_by=admin,
                comments=f"Project restored from Obsolete to {restore_to_status}. {comments}",
                previous_status=old_status,
                new_status=restore_to_status,
                ip_address=request_meta.get('ip_address') if request_meta else None,
                user_agent=request_meta.get('user_agent') if request_meta else None
            )

            # Update ProjectHistory entry
            ProjectHistory.objects.filter(project=project, version=project.version).update(
                approval_status=restore_to_status
            )
            
            logger.info(
                f"Project restored: {project.project_name} V{project.version:03d} "
                f"from {old_status} to {restore_to_status} by {admin.username}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore project {project.id}: {e}")
            return False


class ProjectStatsService:
    """Service for project statistics and reporting"""
    
    @staticmethod
    def get_user_project_stats(user: User) -> Dict[str, Any]:
        """Get project statistics for a specific user"""
        user_projects = Project.objects.filter(submitted_by=user)
        
        return {
            'total_projects': user_projects.count(),
            'draft_projects': user_projects.filter(status='Draft').count(),
            'pending_projects': user_projects.filter(status='Pending_Approval').count(),
            'approved_projects': user_projects.filter(status='Approved').count(),
            'rejected_projects': user_projects.filter(status='Rejected').count(),
            'revision_projects': user_projects.filter(status='Revise_and_Resubmit').count(),
            'recent_projects': user_projects.order_by('-updated_at')[:5]
        }
    
    @staticmethod
    def get_admin_dashboard_stats() -> Dict[str, Any]:
        """Get administrative dashboard statistics"""
        all_projects = Project.objects.all()
        today = timezone.now().date()
        
        return {
            'pending_approvals': all_projects.filter(status='Pending_Approval').count(),
            'total_projects': all_projects.count(),
            'approved_today': all_projects.filter(
                status='Approved', 
                date_reviewed__date=today
            ).count(),
            'rejected_today': all_projects.filter(
                status='Rejected',
                date_reviewed__date=today
            ).count(),
            'recent_submissions': all_projects.filter(
                status='Pending_Approval'
            ).order_by('-date_submitted')[:10]
        }
    
    @staticmethod
    def get_project_group_stats(project_group_id: str) -> Dict[str, Any]:
        """Get statistics for a specific project group"""
        projects = Project.objects.filter(project_group_id=project_group_id)
        
        return {
            'total_versions': projects.count(),
            'latest_version': projects.order_by('-version').first(),
            'approved_versions': projects.filter(status='Approved').count(),
            'version_history': projects.order_by('-version')
        }

    @staticmethod
    def get_project_history_log(project: Project) -> list[Dict[str, Any]]:
        """Get the detailed history log for a specific project."""
        history_logs = ProjectHistory.objects.filter(project=project).order_by('-date_submitted')
        
        log_data = []
        for log in history_logs:
            log_data.append({
                'project_name': log.project.project_name,
                'version': log.version,
                'submitted_by': log.submitted_by.username,
                'date_submitted': log.date_submitted,
                'submission_link': log.submission_link,
                'drawing_qty': log.drawing_qty,
                'drawing_numbers': log.drawing_numbers,
                'receipt_id': log.receipt_id,
                'approval_status': log.approval_status,
            })
        return log_data