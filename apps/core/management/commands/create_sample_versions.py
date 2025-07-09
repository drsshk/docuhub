from django.core.management.base import BaseCommand
from apps.core.models import Version, VersionImprovement


class Command(BaseCommand):
    help = 'Create sample version data for demonstration'

    def handle(self, *args, **options):
        # Create version 1.0.0
        version_100, created = Version.objects.get_or_create(
            version_number='1.0.0',
            defaults={
                'version_type': 'major',
                'description': 'Initial release of DocuHub with core functionality',
                'is_current': False
            }
        )
        
        if created:
            improvements_100 = [
                ('feature', 'User Authentication System', 'Complete user registration, login, and profile management'),
                ('feature', 'Project Management', 'Create, edit, and manage drawing projects with version control'),
                ('feature', 'Drawing Upload System', 'Upload and organize technical drawings with metadata'),
                ('feature', 'Approval Workflow', 'Multi-level approval process for project submissions'),
                ('feature', 'Email Notifications', 'Automated email notifications for project status changes'),
                ('ui', 'Modern Dashboard', 'Clean, responsive dashboard with project overview and statistics'),
            ]
            
            for i, (imp_type, title, description) in enumerate(improvements_100):
                VersionImprovement.objects.create(
                    version=version_100,
                    improvement_type=imp_type,
                    title=title,
                    description=description,
                    order=i
                )
        
        # Create version 1.1.0
        version_110, created = Version.objects.get_or_create(
            version_number='1.1.0',
            defaults={
                'version_type': 'minor',
                'description': 'Enhanced user experience and new reporting features',
                'is_current': True
            }
        )
        
        if created:
            improvements_110 = [
                ('feature', 'Advanced Search & Filters', 'Search projects by name, status, date range with advanced filtering options'),
                ('feature', 'Bulk Project Operations', 'Select and perform actions on multiple projects simultaneously'),
                ('feature', 'Project History Log', 'Detailed audit trail of all project changes and approvals'),
                ('enhancement', 'Improved File Upload', 'Support for larger files and better upload progress indicators'),
                ('enhancement', 'Enhanced Email Templates', 'More professional email templates with better formatting'),
                ('ui', 'Mobile-Responsive Design', 'Optimized interface for tablets and mobile devices'),
                ('performance', 'Database Optimization', 'Improved query performance for large datasets'),
                ('bugfix', 'Fixed File Download Issues', 'Resolved problems with downloading large drawing files'),
            ]
            
            for i, (imp_type, title, description) in enumerate(improvements_110):
                VersionImprovement.objects.create(
                    version=version_110,
                    improvement_type=imp_type,
                    title=title,
                    description=description,
                    order=i
                )
        
        # Create version 1.2.0 (upcoming)
        version_120, created = Version.objects.get_or_create(
            version_number='1.2.0',
            defaults={
                'version_type': 'minor',
                'description': 'Version tracking system and administrative improvements',
                'is_current': False
            }
        )
        
        if created:
            improvements_120 = [
                ('feature', 'Version Tracking System', 'Track application versions with detailed improvement logs'),
                ('feature', 'Advanced Admin Controls', 'Enhanced administrative interface with user management'),
                ('enhancement', 'Improved Navigation', 'Better navigation with version history access'),
                ('security', 'Enhanced Security', 'Improved authentication and permission handling'),
                ('api', 'REST API Endpoints', 'New API endpoints for project data access'),
            ]
            
            for i, (imp_type, title, description) in enumerate(improvements_120):
                VersionImprovement.objects.create(
                    version=version_120,
                    improvement_type=imp_type,
                    title=title,
                    description=description,
                    order=i
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample version data')
        )