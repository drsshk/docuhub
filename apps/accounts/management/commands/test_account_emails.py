from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.notifications.services import BrevoEmailService
from apps.accounts.utils import send_account_setup_email, send_password_reset_email


class Command(BaseCommand):
    help = 'Test account email notifications'

    def add_arguments(self, parser):
        parser.add_argument('--user-email', type=str, help='User email to test with')
        parser.add_argument('--user-id', type=int, help='User ID to test with')

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
        self.stdout.write('\nTesting account email template rendering...')
        try:
            from django.template.loader import render_to_string
            test_context = {
                'user_name': 'Test User',
                'user': type('User', (), {'username': 'testuser', 'email': 'test@example.com'})()
            }
            render_to_string('emails/account_setup.html', test_context)
            render_to_string('emails/password_reset.html', test_context)
            self.stdout.write(self.style.SUCCESS('✓ Account email templates can be rendered'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Template rendering failed: {e}'))
            return
        
        # Find a test user
        test_user = None
        if options.get('user_id'):
            try:
                test_user = User.objects.get(id=options['user_id'])
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {options["user_id"]} not found'))
                return
        elif options.get('user_email'):
            try:
                test_user = User.objects.get(email=options['user_email'])
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with email {options["user_email"]} not found'))
                return
        else:
            # Get the first active user with an email
            test_user = User.objects.filter(is_active=True, email__isnull=False).exclude(email='').first()
            
        if not test_user:
            self.stdout.write(self.style.ERROR('No test user found. Please specify --user-email or --user-id'))
            return
            
        if not test_user.email:
            self.stdout.write(self.style.ERROR(f'User {test_user.username} has no email address'))
            return
            
        self.stdout.write(f'\nTesting with user: {test_user.username} ({test_user.email})')
        
        # Test account setup email
        self.stdout.write('\n--- Testing Account Setup Email ---')
        try:
            token = default_token_generator.make_token(test_user)
            uid = urlsafe_base64_encode(force_bytes(test_user.pk))
            
            success = send_account_setup_email(test_user, token, uid)
            self.stdout.write(
                self.style.SUCCESS('✓ Account setup email sent') if success 
                else self.style.ERROR('✗ Account setup email failed')
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Account setup email error: {e}'))
        
        # Test password reset email
        self.stdout.write('\n--- Testing Password Reset Email ---')
        try:
            temp_password = User.objects.make_random_password(length=10)
            
            success = send_password_reset_email(test_user, temp_password)
            self.stdout.write(
                self.style.SUCCESS('✓ Password reset email sent') if success 
                else self.style.ERROR('✗ Password reset email failed')
            )
            self.stdout.write(f'Temporary password used in test: {temp_password}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Password reset email error: {e}'))
        
        self.stdout.write('\nNote: No actual passwords were changed during this test.')