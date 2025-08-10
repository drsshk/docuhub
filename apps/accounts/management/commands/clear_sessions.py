from django.core.management.base import BaseCommand
from apps.accounts.models import UserSession # Corrected import

class Command(BaseCommand):
    help = 'Clears all existing custom user sessions from the database.'

    def handle(self, *args, **options):
        try:
            UserSession.objects.all().delete() # Corrected model to delete from
            self.stdout.write(self.style.SUCCESS('Successfully cleared all custom user sessions.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error clearing custom user sessions: {e}'))