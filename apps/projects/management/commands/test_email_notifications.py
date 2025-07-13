from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.projects.models import Project
from apps.notifications.services import BrevoEmailService


class Command(BaseCommand):
    help = 'Test email notification system'

    def add_arguments(self, parser):
        parser.add_argument('--project-id', type=str, help='Project ID to test with')
        parser.add_argument('--user-email', type=str, help='User email to test with')

    def handle(self, *args, **options):
        email_service = BrevoEmailService()
        
        # Check if API key is configured
        if not email_service.api_key:
            self.stdout.write(
                self.style.WARNING('BREVO_API_KEY not configured. Email notifications will be logged but not sent.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('BREVO_API_KEY is configured.')
            )
            
        # Test template rendering
        self.stdout.write('\nTesting email template rendering...')
        try:
            from django.template.loader import render_to_string
            test_context = {
                'user_name': 'Test User',
                'project_name': 'Test Project',
                'project_version': 'V001'
            }
            render_to_string('emails/project_submitted.html', test_context)
            self.stdout.write(self.style.SUCCESS('✓ Email templates can be rendered'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Template rendering failed: {e}'))
        
        # Test with a specific project if provided
        if options.get('project_id'):
            try:
                project = Project.objects.get(id=options['project_id'])
                user = project.submitted_by
                
                self.stdout.write(f'Testing with project: {project.project_name} V{project.version}')
                self.stdout.write(f'Project owner: {user.email}')
                
                # Test submission notification
                success = email_service.notify_project_submitted(project, user)
                self.stdout.write(
                    self.style.SUCCESS('✓ Submission notification sent') if success 
                    else self.style.ERROR('✗ Submission notification failed')
                )
                
                # Test admin notification
                admin_users = User.objects.filter(is_staff=True, is_active=True)
                if admin_users.exists():
                    success = email_service.notify_admin_new_submission(project, admin_users)
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Admin notification sent to {admin_users.count()} admins') if success 
                        else self.style.ERROR('✗ Admin notification failed')
                    )
                else:
                    self.stdout.write(self.style.WARNING('No admin users found'))
                    
            except Project.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Project with ID {options["project_id"]} not found'))
        
        else:
            self.stdout.write('No project ID provided. Use --project-id to test with a specific project.')
            
        # Show email template configuration
        from django.conf import settings
        templates = getattr(settings, 'EMAIL_TEMPLATES', {})
        self.stdout.write('\nEmail template configuration:')
        for template_name, template_id in templates.items():
            self.stdout.write(f'  {template_name}: {template_id}')