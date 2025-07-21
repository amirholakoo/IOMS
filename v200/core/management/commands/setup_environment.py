"""
🔧 Management command to setup environment configuration
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil

class Command(BaseCommand):
    help = '🔧 Setup environment configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env',
            type=str,
            choices=['local', 'dev', 'production'],
            default='local',
            help='Environment to setup'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force overwrite existing files'
        )

    def handle(self, *args, **options):
        env = options['env']
        force = options['force']
        
        self.stdout.write(f'🚀 Setting up {env} environment...')
        
        # Create .env file from template
        env_file = f'env.{env}'
        template_file = 'env.example'
        
        if os.path.exists(env_file) and not force:
            self.stdout.write(
                self.style.WARNING(f'⚠️ {env_file} already exists. Use --force to overwrite.')
            )
        else:
            if os.path.exists(template_file):
                shutil.copy(template_file, env_file)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {env_file} from template')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Template file {template_file} not found')
                )
        
        # Create logs directory
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created logs directory: {logs_dir}')
            )
        
        # Environment-specific setup
        if env == 'production':
            self.setup_production()
        elif env == 'dev':
            self.setup_development()
        else:
            self.setup_local()
    
    def setup_production(self):
        """Setup production environment"""
        self.stdout.write('🏭 Setting up production environment...')
        self.stdout.write('⚠️  Remember to:')
        self.stdout.write('   - Change SECRET_KEY in env.production')
        self.stdout.write('   - Update database credentials')
        self.stdout.write('   - Configure real email settings')
        self.stdout.write('   - Set SMS_FALLBACK_TO_FAKE=False')
    
    def setup_development(self):
        """Setup development environment"""
        self.stdout.write('🔧 Setting up development environment...')
        self.stdout.write('✅ Development environment ready!')
        self.stdout.write('📱 SMS server should be running at: http://192.168.1.60:5003')
    
    def setup_local(self):
        """Setup local environment"""
        self.stdout.write('🏠 Setting up local environment...')
        self.stdout.write('✅ Local environment ready!')
        self.stdout.write('📱 For local SMS testing, use SMS_FALLBACK_TO_FAKE=True') 