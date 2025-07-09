from django.core.management.base import BaseCommand
from django.conf import settings
import docuhub


class Command(BaseCommand):
    help = 'Display current application version'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set',
            type=str,
            help='Set new version number',
        )

    def handle(self, *args, **options):
        current_version = docuhub.__version__
        
        if options['set']:
            new_version = options['set']
            version_file = settings.BASE_DIR / 'docuhub' / 'version.py'
            
            with open(version_file, 'w') as f:
                f.write(f"__version__ = '{new_version}'\n")
            
            self.stdout.write(
                self.style.SUCCESS(f'Version updated from {current_version} to {new_version}')
            )
        else:
            self.stdout.write(f'Current version: {current_version}')