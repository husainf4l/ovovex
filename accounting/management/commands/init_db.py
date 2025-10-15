from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Initialize database: create, migrate, and seed with production data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-seed',
            action='store_true',
            help='Skip seeding production data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🚀 INITIALIZING DATABASE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Step 1: Check database connection
        self.stdout.write('📊 Step 1: Checking database connection...')
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS('✅ Database connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database connection failed: {e}'))
            return

        # Step 2: Run migrations
        self.stdout.write('')
        self.stdout.write('🔄 Step 2: Running database migrations...')
        try:
            call_command('migrate', '--noinput')
            self.stdout.write(self.style.SUCCESS('✅ Migrations completed successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Migration failed: {e}'))
            return

        # Step 3: Seed production data
        if not options['skip_seed']:
            self.stdout.write('')
            self.stdout.write('🌱 Step 3: Seeding production data...')
            try:
                call_command('seed_production')
                self.stdout.write(self.style.SUCCESS('✅ Production data seeded successfully'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠️  Seeding completed with warnings: {e}'))
        else:
            self.stdout.write('')
            self.stdout.write('⏭️  Step 3: Skipped (--skip-seed flag set)')

        # Step 4: Check admin user
        self.stdout.write('')
        self.stdout.write('👤 Step 4: Checking admin user...')
        admin_exists = User.objects.filter(username='admin').exists()
        if admin_exists:
            self.stdout.write(self.style.SUCCESS('✅ Admin user exists'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  No admin user found'))

        # Final summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ DATABASE INITIALIZATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Instructions
        if admin_exists:
            self.stdout.write(self.style.SUCCESS('🎉 Your database is ready!'))
            self.stdout.write('')
            self.stdout.write('Next steps:')
            self.stdout.write('  1. Change admin password:')
            self.stdout.write('     python manage.py changepassword admin')
            self.stdout.write('')
            self.stdout.write('  2. Start the server:')
            self.stdout.write('     python manage.py runserver')
            self.stdout.write('')
            self.stdout.write('  3. Login at: http://localhost:8000/en/accounts/login/')
            self.stdout.write('     Username: admin')
            self.stdout.write('     Password: changeme123 (change immediately!)')
        else:
            self.stdout.write(self.style.WARNING('⚠️  Create an admin user:'))
            self.stdout.write('     python manage.py createsuperuser')

        self.stdout.write('')
