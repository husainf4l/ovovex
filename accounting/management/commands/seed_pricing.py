from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from accounting.models import PricingPlan

class Command(BaseCommand):
    help = 'Seed pricing plans data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding pricing plans...')

        # Clear existing plans
        PricingPlan.objects.all().delete()

        # Create pricing plans
        plans_data = [
            {
                'name': 'free',
                'plan_type': 'free',
                'display_name': 'Free',
                'description': 'Perfect for getting started with basic accounting features',
                'price_monthly': Decimal('0.00'),
                'price_yearly': Decimal('0.00'),
                'max_users': 1,
                'max_invoices_per_month': 5,
                'max_storage_gb': 1,
                'api_access': False,
                'priority_support': False,
                'advanced_analytics': False,
                'custom_integrations': False,
                'trial_days': 0,
                'features': {
                    'basic_invoicing': True,
                    'expense_tracking': True,
                    'financial_reports': True,
                    'email_support': True,
                    'mobile_app': True,
                }
            },
            {
                'name': 'starter',
                'plan_type': 'starter',
                'display_name': 'Starter',
                'description': 'Great for small businesses needing advanced accounting features',
                'price_monthly': Decimal('29.00'),
                'price_yearly': Decimal('278.40'),  # 20% discount
                'max_users': 3,
                'max_invoices_per_month': 0,  # Unlimited
                'max_storage_gb': 10,
                'api_access': True,
                'priority_support': True,
                'advanced_analytics': False,
                'custom_integrations': False,
                'trial_days': 14,
                'features': {
                    'unlimited_invoices': True,
                    'advanced_expense_tracking': True,
                    'multi_currency': True,
                    'bank_reconciliation': True,
                    'priority_email_support': True,
                    'api_access': True,
                    'mobile_app': True,
                    'basic_reporting': True,
                }
            },
            {
                'name': 'professional',
                'plan_type': 'professional',
                'display_name': 'Professional',
                'description': 'For growing businesses with advanced analytics and automation needs',
                'price_monthly': Decimal('79.00'),
                'price_yearly': Decimal('758.40'),  # 20% discount
                'max_users': 10,
                'max_invoices_per_month': 0,  # Unlimited
                'max_storage_gb': 50,
                'api_access': True,
                'priority_support': True,
                'advanced_analytics': True,
                'custom_integrations': False,
                'trial_days': 14,
                'features': {
                    'everything_in_starter': True,
                    'advanced_analytics': True,
                    'inventory_management': True,
                    'project_accounting': True,
                    'custom_workflows': True,
                    'phone_support': True,
                    'advanced_reporting': True,
                    'budget_planning': True,
                    'multi_company': True,
                }
            },
            {
                'name': 'enterprise',
                'plan_type': 'enterprise',
                'display_name': 'Enterprise',
                'description': 'For large organizations requiring custom integrations and dedicated support',
                'price_monthly': Decimal('199.00'),
                'price_yearly': Decimal('1910.40'),  # 20% discount
                'max_users': 0,  # Unlimited
                'max_invoices_per_month': 0,  # Unlimited
                'max_storage_gb': 0,  # Unlimited
                'api_access': True,
                'priority_support': True,
                'advanced_analytics': True,
                'custom_integrations': True,
                'trial_days': 30,
                'features': {
                    'everything_in_professional': True,
                    'unlimited_users': True,
                    'unlimited_storage': True,
                    'custom_integrations': True,
                    'dedicated_account_manager': True,
                    'sla_guarantees': True,
                    'premium_support_24_7': True,
                    'custom_training': True,
                    'advanced_security': True,
                    'white_label_option': True,
                }
            }
        ]

        for plan_data in plans_data:
            plan, created = PricingPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'Created pricing plan: {plan.display_name}')
            else:
                # Update existing plan
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
                self.stdout.write(f'Updated pricing plan: {plan.display_name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded pricing plans!'))