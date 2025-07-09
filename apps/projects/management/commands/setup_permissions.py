"""
Management command to set up project permissions and groups.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from apps.projects.permissions import setup_project_permissions


class Command(BaseCommand):
    help = 'Set up project permissions and user groups'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--assign-existing-staff',
            action='store_true',
            help='Assign existing staff users to Project Managers group',
        )
        parser.add_argument(
            '--assign-superusers',
            action='store_true',
            help='Assign superusers to Project Administrators group',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up project permissions and groups...')
        
        try:
            # Create permissions and groups
            created_permissions, created_groups = setup_project_permissions()
            
            if created_permissions:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {len(created_permissions)} custom permissions:'
                    )
                )
                for perm in created_permissions:
                    self.stdout.write(f'  - {perm.name} ({perm.codename})')
            else:
                self.stdout.write('All permissions already exist.')
            
            if created_groups:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {len(created_groups)} user groups:'
                    )
                )
                for group in created_groups:
                    self.stdout.write(f'  - {group.name}')
            else:
                self.stdout.write('All groups already exist.')
            
            # Assign existing users if requested
            if options['assign_existing_staff']:
                self.assign_staff_users()
            
            if options['assign_superusers']:
                self.assign_superusers()
            
            self.stdout.write(
                self.style.SUCCESS('Project permissions setup completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up permissions: {e}')
            )
    
    def assign_staff_users(self):
        """Assign existing staff users to Project Managers group"""
        try:
            managers_group = Group.objects.get(name='Project Managers')
            staff_users = User.objects.filter(is_staff=True, is_superuser=False)
            
            assigned_count = 0
            for user in staff_users:
                if not managers_group.user_set.filter(id=user.id).exists():
                    managers_group.user_set.add(user)
                    assigned_count += 1
                    self.stdout.write(f'  Assigned {user.username} to Project Managers')
            
            if assigned_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Assigned {assigned_count} staff users to Project Managers group'
                    )
                )
            else:
                self.stdout.write('No staff users needed assignment.')
                
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Project Managers group not found!')
            )
    
    def assign_superusers(self):
        """Assign superusers to Project Administrators group"""
        try:
            admins_group = Group.objects.get(name='Project Administrators')
            superusers = User.objects.filter(is_superuser=True)
            
            assigned_count = 0
            for user in superusers:
                if not admins_group.user_set.filter(id=user.id).exists():
                    admins_group.user_set.add(user)
                    assigned_count += 1
                    self.stdout.write(f'  Assigned {user.username} to Project Administrators')
            
            if assigned_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Assigned {assigned_count} superusers to Project Administrators group'
                    )
                )
            else:
                self.stdout.write('No superusers needed assignment.')
                
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Project Administrators group not found!')
            )