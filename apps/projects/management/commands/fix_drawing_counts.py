from django.core.management.base import BaseCommand
from apps.projects.models import Project


class Command(BaseCommand):
    help = 'Fix drawing counts for all projects'

    def handle(self, *args, **options):
        projects = Project.objects.all()
        fixed_count = 0
        
        for project in projects:
            old_count = project.no_of_drawings
            correct_count = project.drawings.filter(status='Active').count()
            
            if old_count != correct_count:
                project.no_of_drawings = correct_count
                project.save(update_fields=['no_of_drawings', 'updated_at'])
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fixed {project.project_name} V{project.version}: '
                        f'{old_count} -> {correct_count} drawings'
                    )
                )
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully fixed drawing counts for {fixed_count} projects'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All project drawing counts are already correct')
            )