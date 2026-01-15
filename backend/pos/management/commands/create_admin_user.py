from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import getpass


class Command(BaseCommand):
    help = 'Create an admin user for VARANDA POS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the admin user',
            default='admin@gmail.com'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the admin user',
            default=None
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the admin user (defaults to email)',
            default=None
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if user exists (will update password)',
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password'] or '12345!'
        username = options['username'] or email
        force = options['force']

        self.stdout.write(
            self.style.SUCCESS('🚀 Creating admin user for VARANDA POS')
        )
        
        # Validate email format
        if '@' not in email:
            self.stdout.write(
                self.style.ERROR('❌ Invalid email format')
            )
            return
        
        # Validate password meets Django requirements
        try:
            validate_password(password)
        except ValidationError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Password validation failed: {", ".join(e.messages)}')
            )
            self.stdout.write(
                self.style.WARNING('💡 Password requirements:')
            )
            self.stdout.write('   - At least 8 characters long')
            self.stdout.write('   - Cannot be too common')
            self.stdout.write('   - Cannot be entirely numeric')
            self.stdout.write('   - Should contain mix of letters, numbers, and symbols')
            return

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            if not force:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  User "{username}" already exists!')
                )
                self.stdout.write(
                    self.style.WARNING('   Use --force flag to update the password')
                )
                return
            else:
                # Update existing user
                user = User.objects.get(username=username)
                user.email = email
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Updated existing admin user!')
                )
        else:
            # Create new user
            try:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Admin user created successfully!')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to create user: {str(e)}')
                )
                return

        # Display user details
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('👤 Admin User Details:'))
        self.stdout.write(f'   📧 Email: {email}')
        self.stdout.write(f'   👤 Username: {username}')
        self.stdout.write(f'   🔑 Password: {password}')
        self.stdout.write(f'   🔐 Is Superuser: Yes')
        self.stdout.write(f'   👔 Is Staff: Yes')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 You can now login to the admin panel at:'))
        self.stdout.write('   🌐 http://localhost:8000/admin/')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🔐 API Authentication endpoints:'))
        self.stdout.write('   📝 Login: POST http://localhost:8000/api/token/')
        self.stdout.write('   🔄 Refresh: POST http://localhost:8000/api/token/refresh/')
        self.stdout.write('')
        
        # Test password strength
        self.stdout.write(self.style.WARNING('🔒 Password Security Check:'))
        
        security_score = 0
        feedback = []
        
        if len(password) >= 12:
            security_score += 2
            feedback.append('✅ Good length (12+ characters)')
        elif len(password) >= 8:
            security_score += 1
            feedback.append('⚠️  Minimum length (8+ characters)')
        else:
            feedback.append('❌ Too short (less than 8 characters)')
        
        if any(c.isupper() for c in password):
            security_score += 1
            feedback.append('✅ Contains uppercase letters')
        else:
            feedback.append('⚠️  No uppercase letters')
            
        if any(c.islower() for c in password):
            security_score += 1
            feedback.append('✅ Contains lowercase letters')
        else:
            feedback.append('⚠️  No lowercase letters')
            
        if any(c.isdigit() for c in password):
            security_score += 1
            feedback.append('✅ Contains numbers')
        else:
            feedback.append('⚠️  No numbers')
            
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            security_score += 1
            feedback.append('✅ Contains special characters')
        else:
            feedback.append('⚠️  No special characters')
        
        for item in feedback:
            self.stdout.write(f'   {item}')
            
        if security_score >= 5:
            self.stdout.write(self.style.SUCCESS('   🛡️  Password strength: STRONG'))
        elif security_score >= 3:
            self.stdout.write(self.style.WARNING('   🔶 Password strength: MEDIUM'))
        else:
            self.stdout.write(self.style.ERROR('   ⚠️  Password strength: WEAK'))
            
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✨ Admin user setup complete!'))