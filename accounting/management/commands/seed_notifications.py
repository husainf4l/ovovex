from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import Notification
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Seed database with sample notifications for testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding notifications...')

        # Get admin user
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user not found. Please run seed_demo_data first.'))
            return

        # Sample notification data
        notifications_data = [
            {
                'title': 'Tax Filing Deadline Approaching',
                'message': 'Your quarterly VAT return is due in 5 days. Don\'t forget to file before October 15th.',
                'notification_type': 'warning',
                'action_url': '/tax-center/',
                'action_text': 'File Now',
                'is_read': False,
                'created_at': datetime.now() - timedelta(hours=2)
            },
            {
                'title': 'Invoice Payment Overdue',
                'message': 'Invoice INV-2025-038 ($5,420) from TechCorp Solutions is now 7 days overdue.',
                'notification_type': 'error',
                'action_url': '/invoices/',
                'action_text': 'Send Reminder',
                'is_read': False,
                'created_at': datetime.now() - timedelta(hours=4)
            },
            {
                'title': 'Bank Reconciliation Completed',
                'message': 'Monthly bank reconciliation for Checking Account has been completed. 3 transactions were auto-matched.',
                'notification_type': 'success',
                'action_url': '/bank-reconciliation/',
                'action_text': 'View Details',
                'is_read': True,
                'created_at': datetime.now() - timedelta(hours=6)
            },
            {
                'title': 'New Expense Approved',
                'message': 'Your office supplies expense ($2,340) has been approved and processed.',
                'notification_type': 'success',
                'action_url': '/expense-management/',
                'action_text': 'View Expense',
                'is_read': True,
                'created_at': datetime.now() - timedelta(hours=8)
            },
            {
                'title': 'Cash Flow Alert',
                'message': 'Your cash balance is projected to drop below $10,000 in the next 7 days.',
                'notification_type': 'warning',
                'action_url': '/cash-flow/',
                'action_text': 'Review Forecast',
                'is_read': False,
                'created_at': datetime.now() - timedelta(hours=12)
            },
            {
                'title': 'Monthly Report Available',
                'message': 'Your September 2025 financial summary and KPIs are now available for review.',
                'notification_type': 'info',
                'action_url': '/financial-statements/',
                'action_text': 'View Report',
                'is_read': False,
                'created_at': datetime.now() - timedelta(hours=18)
            },
            {
                'title': 'AI Insight: Revenue Opportunity',
                'message': 'AI analysis detected a 15% revenue optimization opportunity through pricing adjustments.',
                'notification_type': 'info',
                'action_url': '/ai-insights/',
                'action_text': 'View Insight',
                'is_read': False,
                'created_at': datetime.now() - timedelta(hours=24)
            },
            {
                'title': 'System Backup Completed',
                'message': 'Daily automated backup completed successfully. All data is secure.',
                'notification_type': 'success',
                'action_url': '/settings/',
                'action_text': 'Backup Settings',
                'is_read': True,
                'created_at': datetime.now() - timedelta(hours=26)
            },
            {
                'title': 'New Client Onboarded',
                'message': 'Welcome email sent to XYZ Industries. Their account is now active.',
                'notification_type': 'info',
                'action_url': '/customer-portal/',
                'action_text': 'View Client',
                'is_read': True,
                'created_at': datetime.now() - timedelta(hours=30)
            },
            {
                'title': 'Expense Policy Reminder',
                'message': 'Remember to submit receipts for expenses over $100 within 30 days for reimbursement.',
                'notification_type': 'info',
                'action_url': '/expense-management/',
                'action_text': 'Submit Receipt',
                'is_read': False,
                'created_at': datetime.now() - timedelta(hours=36)
            }
        ]

        created_count = 0
        for notif_data in notifications_data:
            notification, created = Notification.objects.get_or_create(
                user=admin_user,
                title=notif_data['title'],
                message=notif_data['message'],
                defaults={
                    'notification_type': notif_data['notification_type'],
                    'action_url': notif_data['action_url'],
                    'action_text': notif_data['action_text'],
                    'is_read': notif_data['is_read'],
                    'created_at': notif_data['created_at'],
                    'updated_at': notif_data['created_at']
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} notifications'))

        # Update timestamps to spread them out
        notifications = Notification.objects.filter(user=admin_user).order_by('-created_at')
        base_time = datetime.now()
        for i, notification in enumerate(notifications[:10]):
            notification.created_at = base_time - timedelta(hours=i*2)
            notification.updated_at = notification.created_at
            notification.save()

        self.stdout.write(self.style.SUCCESS('Notification timestamps updated'))