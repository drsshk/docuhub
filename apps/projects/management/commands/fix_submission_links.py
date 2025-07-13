from django.core.management.base import BaseCommand
from apps.projects.models import ProjectHistory


class Command(BaseCommand):
    help = 'Fix empty submission links in project history'

    def handle(self, *args, **options):
        history_entries = ProjectHistory.objects.filter(submission_link__in=['', None])
        fixed_count = 0
        
        for entry in history_entries:
            if entry.project:
                entry.submission_link = entry.project.get_absolute_url()
                entry.save(update_fields=['submission_link'])
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fixed submission link for {entry.project.project_name} V{entry.version}'
                    )
                )
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully fixed submission links for {fixed_count} project history entries'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All project history submission links are already set')
            )