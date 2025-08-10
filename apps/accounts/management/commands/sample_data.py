from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.projects.models import Project, Drawing
from apps.accounts.models import UserProfile
import random

class Command(BaseCommand):
    help = 'Create sample data for testing'
    
    def handle(self, *args, **options):
        # Create test users
        if not User.objects.filter(username='testuser').exists():
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(f'Created user: {user.username}')
        
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(f'Created admin: {admin.username}')
        
        # Create sample projects
        user = User.objects.get(username='testuser')
        
        sample_projects = [
            {
                'name': 'Office Building Renovation',
                'description': 'Complete renovation of the main office building including HVAC, electrical, and structural modifications.',
                'department': 'Facilities Management',
                'priority': 'High'
            },
            {
                'name': 'Parking Garage Extension',
                'description': 'Addition of 200 parking spaces with new lighting and security systems.',
                'department': 'Construction',
                'priority': 'Normal'
            },
            {
                'name': 'Laboratory Equipment Installation',
                'description': 'Installation of new research equipment in the chemistry laboratory.',
                'department': 'Research & Development',
                'priority': 'Urgent'
            }
        ]
        
        for project_data in sample_projects:
            if not Project.objects.filter(project_name=project_data['name']).exists():
                project = Project.objects.create(
                    project_name=project_data['name'],
                    project_description=project_data['description'],
                    client_department=project_data['department'],
                    project_priority=project_data['priority'],
                    submitted_by=user,
                    status=random.choice(['Draft', 'Pending_Approval', 'Approved'])
                )
                
                # Add sample drawings
                drawing_types = [
                    ('A001', 'Floor Plan - Ground Level', 'Architectural'),
                    ('A002', 'Floor Plan - Second Level', 'Architectural'),
                    ('S001', 'Foundation Plan', 'Structural'),
                    ('M001', 'HVAC Layout', 'Mechanical'),
                    ('E001', 'Electrical Distribution', 'Electrical')
                ]
                
                for drawing_no, title, discipline in drawing_types[:random.randint(2, 4)]:
                    Drawing.objects.create(
                        project=project,
                        drawing_no=drawing_no,
                        drawing_title=title,
                        discipline=discipline,
                        drawing_list_link=f'https://example.com/drawings/{drawing_no}.pdf',
                        added_by=user
                    )
                
                self.stdout.write(f'Created project: {project.project_name}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))