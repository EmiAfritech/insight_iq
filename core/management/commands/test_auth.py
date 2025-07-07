from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()

class Command(BaseCommand):
    help = 'Test the authentication flow'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Test email address', default='test@example.com')
        parser.add_argument('--password', type=str, help='Test password', default='testpass123')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        
        self.stdout.write(self.style.SUCCESS(f'Testing authentication flow for {email}'))
        
        # Create a test client
        client = Client()
        
        # Test signup page loads
        try:
            response = client.get('/accounts/signup/')
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✓ Signup page loads successfully'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Signup page failed: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Signup page error: {e}'))
        
        # Test login page loads
        try:
            response = client.get('/accounts/login/')
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✓ Login page loads successfully'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Login page failed: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Login page error: {e}'))
        
        # Test if user already exists
        try:
            user = User.objects.get(email=email)
            self.stdout.write(self.style.WARNING(f'User {email} already exists'))
        except User.DoesNotExist:
            # Test user creation via signup form
            try:
                signup_data = {
                    'email': email,
                    'password1': password,
                    'password2': password,
                }
                response = client.post('/accounts/signup/', signup_data)
                if response.status_code in [200, 302]:
                    self.stdout.write(self.style.SUCCESS('✓ User signup successful'))
                    user = User.objects.get(email=email)
                    self.stdout.write(self.style.SUCCESS(f'✓ User created: {user.email}'))
                else:
                    self.stdout.write(self.style.ERROR(f'✗ Signup failed: {response.status_code}'))
                    self.stdout.write(self.style.ERROR(f'Response content: {response.content.decode()}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Signup error: {e}'))
        
        # Test login
        try:
            login_data = {
                'login': email,
                'password': password,
            }
            response = client.post('/accounts/login/', login_data)
            if response.status_code in [200, 302]:
                self.stdout.write(self.style.SUCCESS('✓ User login successful'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Login failed: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Login error: {e}'))
        
        # Test dashboard access
        try:
            response = client.get('/dashboard/')
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✓ Dashboard accessible'))
            elif response.status_code == 302:
                self.stdout.write(self.style.WARNING('Dashboard redirected (normal if not logged in)'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Dashboard failed: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Dashboard error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Authentication flow test completed'))
