from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import *
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
import random
import json

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive dashboard data and metrics'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Starting Dashboard Data Seeding'))
        self.stdout.write(self.style.SUCCESS('='*60))

        # Get or create admin user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ovovex.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created admin user'))
        else:
            self.stdout.write('✓ Using existing admin user')

        # Clear existing dashboard data
        self.stdout.write('\nClearing existing dashboard data...')
        models_to_clear = [
            DashboardKPIMetric, DashboardWidget, DashboardChartData,
            DashboardAlert, DashboardActivity, DashboardSettings
        ]
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            if count > 0:
                self.stdout.write(f'  Cleared {count} {model.__name__} records')

        # Seed KPI Metrics
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Dashboard KPI Metrics')
        self.stdout.write('='*60)
        kpis = self._seed_kpi_metrics(user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(kpis)} KPI metrics'))

        # Seed Dashboard Widgets
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Dashboard Widgets')
        self.stdout.write('='*60)
        widgets = self._seed_dashboard_widgets(user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(widgets)} dashboard widgets'))

        # Seed Chart Data
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Chart Data')
        self.stdout.write('='*60)
        chart_data_count = self._seed_chart_data(widgets)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {chart_data_count} chart data points'))

        # Seed Alerts
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Dashboard Alerts')
        self.stdout.write('='*60)
        alerts = self._seed_alerts(user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(alerts)} dashboard alerts'))

        # Seed Activities
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Dashboard Activities')
        self.stdout.write('='*60)
        activities = self._seed_activities(user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(activities)} activity records'))

        # Seed Dashboard Settings
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SEEDING: Dashboard Settings')
        self.stdout.write('='*60)
        settings = self._seed_dashboard_settings(user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(settings)} dashboard settings'))

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Dashboard data seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))

    def _seed_kpi_metrics(self, user):
        """Seed comprehensive KPI metrics with real business data"""
        kpi_data = [
            {
                'name': 'total_revenue',
                'display_name': 'Total Revenue',
                'description': 'Total revenue from all sources',
                'metric_type': 'CURRENCY',
                'current_value': Decimal('2456789.50'),
                'previous_value': Decimal('2189456.75'),
                'prefix': '$',
                'display_order': 1
            },
            {
                'name': 'total_expenses',
                'display_name': 'Total Expenses',
                'description': 'Total operating expenses',
                'metric_type': 'CURRENCY',
                'current_value': Decimal('1876543.25'),
                'previous_value': Decimal('1923456.80'),
                'prefix': '$',
                'display_order': 2
            },
            {
                'name': 'net_profit',
                'display_name': 'Net Profit',
                'description': 'Net profit after all expenses',
                'metric_type': 'CURRENCY',
                'current_value': Decimal('580246.25'),
                'previous_value': Decimal('266000.00'),
                'prefix': '$',
                'display_order': 3
            },
            {
                'name': 'profit_margin',
                'display_name': 'Profit Margin',
                'description': 'Net profit as percentage of revenue',
                'metric_type': 'PERCENTAGE',
                'current_value': Decimal('23.60'),
                'previous_value': Decimal('12.15'),
                'suffix': '%',
                'display_order': 4
            },
            {
                'name': 'accounts_receivable',
                'display_name': 'Accounts Receivable',
                'description': 'Total outstanding customer invoices',
                'metric_type': 'CURRENCY',
                'current_value': Decimal('456789.30'),
                'previous_value': Decimal('523456.75'),
                'prefix': '$',
                'display_order': 5
            },
            {
                'name': 'accounts_payable',
                'display_name': 'Accounts Payable',
                'description': 'Total outstanding vendor bills',
                'metric_type': 'CURRENCY',
                'current_value': Decimal('234567.80'),
                'previous_value': Decimal('289456.25'),
                'prefix': '$',
                'display_order': 6
            },
            {
                'name': 'cash_flow',
                'display_name': 'Operating Cash Flow',
                'description': 'Cash generated from operations',
                'metric_type': 'CURRENCY',
                'current_value': Decimal('678945.60'),
                'previous_value': Decimal('543678.90'),
                'prefix': '$',
                'display_order': 7
            },
            {
                'name': 'inventory_value',
                'display_name': 'Inventory Value',
                'description': 'Total value of current inventory',
                'metric_type': 'CURRENCY',
                'current_value': Decimal('345678.90'),
                'previous_value': Decimal('412345.60'),
                'prefix': '$',
                'display_order': 8
            },
            {
                'name': 'customer_count',
                'display_name': 'Active Customers',
                'description': 'Number of active customers',
                'metric_type': 'NUMBER',
                'current_value': Decimal('247'),
                'previous_value': Decimal('223'),
                'display_order': 9
            },
            {
                'name': 'employee_count',
                'display_name': 'Total Employees',
                'description': 'Number of employees',
                'metric_type': 'NUMBER',
                'current_value': Decimal('45'),
                'previous_value': Decimal('42'),
                'display_order': 10
            },
            {
                'name': 'avg_invoice_payment_time',
                'display_name': 'Avg Payment Time',
                'description': 'Average days to receive payment',
                'metric_type': 'NUMBER',
                'current_value': Decimal('28.5'),
                'previous_value': Decimal('32.2'),
                'suffix': ' days',
                'display_order': 11
            },
            {
                'name': 'budget_variance',
                'display_name': 'Budget Variance',
                'description': 'Variance from budgeted expenses',
                'metric_type': 'PERCENTAGE',
                'current_value': Decimal('-3.2'),
                'previous_value': Decimal('5.8'),
                'suffix': '%',
                'display_order': 12
            }
        ]

        kpis = []
        for data in kpi_data:
            kpi = DashboardKPIMetric.objects.create(
                name=data['name'],
                display_name=data['display_name'],
                description=data['description'],
                metric_type=data['metric_type'],
                current_value=data['current_value'],
                previous_value=data['previous_value'],
                prefix=data.get('prefix'),
                suffix=data.get('suffix'),
                display_order=data['display_order']
            )
            kpi.calculate_trend()
            kpi.save()
            kpis.append(kpi)

        return kpis

    def _seed_dashboard_widgets(self, user):
        """Seed dashboard widgets with various types"""
        widgets_data = [
            {
                'title': 'Revenue Overview',
                'widget_type': 'CHART',
                'chart_type': 'LINE',
                'position_x': 0,
                'position_y': 0,
                'width': 2,
                'height': 1,
                'data_source': 'revenue_trends',
                'config': {'period': 'monthly', 'show_trend': True}
            },
            {
                'title': 'Profit & Loss',
                'widget_type': 'CHART',
                'chart_type': 'BAR',
                'position_x': 2,
                'position_y': 0,
                'width': 2,
                'height': 1,
                'data_source': 'pnl_summary',
                'config': {'show_variance': True}
            },
            {
                'title': 'Cash Flow Statement',
                'widget_type': 'CHART',
                'chart_type': 'AREA',
                'position_x': 0,
                'position_y': 1,
                'width': 2,
                'height': 1,
                'data_source': 'cash_flow_data',
                'config': {'cumulative': True}
            },
            {
                'title': 'Top Customers',
                'widget_type': 'TABLE',
                'position_x': 2,
                'position_y': 1,
                'width': 2,
                'height': 1,
                'data_source': 'customer_revenue',
                'config': {'limit': 10, 'sort_by': 'revenue'}
            },
            {
                'title': 'Expense Breakdown',
                'widget_type': 'CHART',
                'chart_type': 'PIE',
                'position_x': 0,
                'position_y': 2,
                'width': 1,
                'height': 1,
                'data_source': 'expense_categories',
                'config': {'show_percentage': True}
            },
            {
                'title': 'Recent Transactions',
                'widget_type': 'TABLE',
                'position_x': 1,
                'position_y': 2,
                'width': 2,
                'height': 1,
                'data_source': 'recent_transactions',
                'config': {'limit': 15}
            },
            {
                'title': 'Budget vs Actual',
                'widget_type': 'CHART',
                'chart_type': 'BAR',
                'position_x': 3,
                'position_y': 2,
                'width': 1,
                'height': 1,
                'data_source': 'budget_comparison',
                'config': {'show_variance': True}
            },
            {
                'title': 'Key Metrics',
                'widget_type': 'SUMMARY',
                'position_x': 0,
                'position_y': 3,
                'width': 4,
                'height': 1,
                'data_source': 'kpi_summary',
                'config': {'metrics': ['total_revenue', 'net_profit', 'accounts_receivable']}
            }
        ]

        widgets = []
        for data in widgets_data:
            widget = DashboardWidget.objects.create(
                title=data['title'],
                widget_type=data['widget_type'],
                chart_type=data.get('chart_type'),
                position_x=data['position_x'],
                position_y=data['position_y'],
                width=data['width'],
                height=data['height'],
                data_source=data.get('data_source'),
                config=data.get('config'),
                created_by=user
            )
            widgets.append(widget)

        return widgets

    def _seed_chart_data(self, widgets):
        """Seed chart data for various widgets"""
        total_data_points = 0

        # Revenue trends data (monthly for 12 months)
        revenue_widget = widgets[0]  # Revenue Overview
        base_date = timezone.now().date().replace(day=1)
        for i in range(12):
            month_date = base_date - timedelta(days=30*i)
            revenue_value = Decimal(str(random.randint(150000, 250000)))
            DashboardChartData.objects.create(
                widget=revenue_widget,
                label=month_date.strftime('%b %Y'),
                value=revenue_value,
                date=month_date,
                period='monthly',
                sort_order=12-i
            )
            total_data_points += 1

        # P&L data
        pnl_widget = widgets[1]  # Profit & Loss
        pnl_categories = [
            ('Revenue', Decimal('2456789.50')),
            ('COGS', Decimal('1234567.25')),
            ('Gross Profit', Decimal('1222222.25')),
            ('Operating Expenses', Decimal('642976.00')),
            ('Net Profit', Decimal('580246.25'))
        ]
        for i, (category, value) in enumerate(pnl_categories):
            DashboardChartData.objects.create(
                widget=pnl_widget,
                label=category,
                value=value,
                category='income_statement',
                sort_order=i
            )
            total_data_points += 1

        # Cash flow data
        cash_widget = widgets[2]  # Cash Flow
        cash_flow_data = [
            ('Operating Activities', Decimal('678945.60')),
            ('Investing Activities', Decimal('-234567.80')),
            ('Financing Activities', Decimal('-123456.75')),
            ('Net Cash Flow', Decimal('320921.05'))
        ]
        for i, (activity, value) in enumerate(cash_flow_data):
            DashboardChartData.objects.create(
                widget=cash_widget,
                label=activity,
                value=value,
                category='cash_flow',
                sort_order=i
            )
            total_data_points += 1

        # Expense breakdown (pie chart)
        expense_widget = widgets[4]  # Expense Breakdown
        expense_data = [
            ('Salaries', Decimal('850000.00')),
            ('Rent', Decimal('150000.00')),
            ('Marketing', Decimal('120000.00')),
            ('Utilities', Decimal('45000.00')),
            ('Office Supplies', Decimal('35000.00')),
            ('Professional Services', Decimal('75000.00')),
            ('Other', Decimal('95000.00'))
        ]
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#FF6384']
        for i, (category, value) in enumerate(expense_data):
            DashboardChartData.objects.create(
                widget=expense_widget,
                label=category,
                value=value,
                category='expenses',
                color=colors[i % len(colors)],
                sort_order=i
            )
            total_data_points += 1

        # Budget vs Actual
        budget_widget = widgets[6]  # Budget vs Actual
        budget_data = [
            ('Q1 Budget', Decimal('450000.00')),
            ('Q1 Actual', Decimal('432000.00')),
            ('Q2 Budget', Decimal('480000.00')),
            ('Q2 Actual', Decimal('523456.00')),
            ('Q3 Budget', Decimal('520000.00')),
            ('Q3 Actual', Decimal('498765.00'))
        ]
        for i, (period, value) in enumerate(budget_data):
            category = 'budget' if 'Budget' in period else 'actual'
            DashboardChartData.objects.create(
                widget=budget_widget,
                label=period,
                value=value,
                category=category,
                sort_order=i
            )
            total_data_points += 1

        return total_data_points

    def _seed_alerts(self, user):
        """Seed dashboard alerts with various priorities"""
        alerts_data = [
            {
                'title': 'Invoice Payment Overdue',
                'message': 'Invoice INV-2025-001 for $15,750.00 from ABC Corporation is 5 days overdue.',
                'alert_type': 'WARNING',
                'priority': 'HIGH',
                'related_model': 'Invoice',
                'related_id': 1
            },
            {
                'title': 'Low Cash Balance Alert',
                'message': 'Operating cash balance has fallen below $50,000 threshold.',
                'alert_type': 'ERROR',
                'priority': 'CRITICAL',
                'related_model': 'Account'
            },
            {
                'title': 'Budget Limit Exceeded',
                'message': 'Marketing expenses have exceeded 90% of quarterly budget.',
                'alert_type': 'WARNING',
                'priority': 'MEDIUM',
                'related_model': 'Budget'
            },
            {
                'title': 'Tax Filing Deadline',
                'message': 'Q2 tax return is due in 7 days. Please prepare documentation.',
                'alert_type': 'INFO',
                'priority': 'MEDIUM',
                'related_model': 'TaxReturn'
            },
            {
                'title': 'New Customer Added',
                'message': 'Welcome Tech Solutions Ltd as a new customer!',
                'alert_type': 'SUCCESS',
                'priority': 'LOW'
            },
            {
                'title': 'System Maintenance',
                'message': 'Scheduled maintenance will occur tonight from 2-4 AM EST.',
                'alert_type': 'INFO',
                'priority': 'LOW'
            },
            {
                'title': 'Payment Received',
                'message': 'Payment of $25,000 received from XYZ Industries.',
                'alert_type': 'SUCCESS',
                'priority': 'MEDIUM',
                'related_model': 'Payment'
            },
            {
                'title': 'Inventory Reorder Alert',
                'message': 'Office supplies inventory is below reorder point.',
                'alert_type': 'WARNING',
                'priority': 'MEDIUM',
                'related_model': 'InventoryItem'
            }
        ]

        alerts = []
        for data in alerts_data:
            alert = DashboardAlert.objects.create(
                title=data['title'],
                message=data['message'],
                alert_type=data['alert_type'],
                priority=data['priority'],
                related_model=data.get('related_model'),
                related_id=data.get('related_id'),
                user=user,
                auto_dismiss=data.get('auto_dismiss', False),
                dismiss_after_hours=data.get('dismiss_after_hours', 24)
            )
            alerts.append(alert)

        return alerts

    def _seed_activities(self, user):
        """Seed recent activity feed"""
        activities_data = [
            {
                'activity_type': 'INVOICE_CREATED',
                'title': 'Invoice INV-2025-003 created',
                'description': 'Created invoice for $8,750.00 to Tech Solutions Ltd',
                'amount': Decimal('8750.00'),
                'related_model': 'Invoice',
                'related_id': 3
            },
            {
                'activity_type': 'PAYMENT_RECEIVED',
                'title': 'Payment received from ABC Corporation',
                'description': 'Received $15,750.00 payment for Invoice INV-2025-001',
                'amount': Decimal('15750.00'),
                'related_model': 'Payment'
            },
            {
                'activity_type': 'BILL_PAID',
                'title': 'Vendor bill paid',
                'description': 'Paid $12,500.00 to Office Supplies Co for bill BILL-2025-002',
                'amount': Decimal('12500.00'),
                'related_model': 'Bill',
                'related_id': 2
            },
            {
                'activity_type': 'JOURNAL_POSTED',
                'title': 'Journal entry posted',
                'description': 'Posted monthly depreciation journal entry for $8,750.00',
                'amount': Decimal('8750.00'),
                'related_model': 'JournalEntry'
            },
            {
                'activity_type': 'EXPENSE_APPROVED',
                'title': 'Expense approved',
                'description': 'Approved travel expense for $2,450.00',
                'amount': Decimal('2450.00'),
                'related_model': 'Expense'
            },
            {
                'activity_type': 'ASSET_ADDED',
                'title': 'Fixed asset added',
                'description': 'Added new server equipment worth $15,000.00',
                'amount': Decimal('15000.00'),
                'related_model': 'FixedAsset'
            },
            {
                'activity_type': 'BUDGET_CREATED',
                'title': 'Budget created',
                'description': 'Created FY2025 annual budget with total $2,450,000.00',
                'amount': Decimal('2450000.00'),
                'related_model': 'Budget'
            },
            {
                'activity_type': 'TAX_RETURN_FILED',
                'title': 'Tax return filed',
                'description': 'Filed Q1 corporate tax return',
                'related_model': 'TaxReturn'
            },
            {
                'activity_type': 'INVOICE_PAID',
                'title': 'Invoice marked as paid',
                'description': 'Invoice INV-2025-002 fully paid by Global Trading Inc',
                'amount': Decimal('22500.00'),
                'related_model': 'Invoice',
                'related_id': 2
            },
            {
                'activity_type': 'PAYMENT_MADE',
                'title': 'Payment made to vendor',
                'description': 'Paid $8,750.00 to Legal Services LLP',
                'amount': Decimal('8750.00'),
                'related_model': 'Payment'
            }
        ]

        activities = []
        base_time = timezone.now()
        for i, data in enumerate(activities_data):
            # Create activities with different timestamps
            created_at = base_time - timedelta(hours=i*2, minutes=random.randint(0, 59))

            activity = DashboardActivity.objects.create(
                activity_type=data['activity_type'],
                title=data['title'],
                description=data['description'],
                related_model=data.get('related_model'),
                related_id=data.get('related_id'),
                amount=data.get('amount'),
                currency=data.get('currency', 'USD'),
                user=user,
                created_at=created_at
            )
            activities.append(activity)

        return activities

    def _seed_dashboard_settings(self, user):
        """Seed dashboard settings for the user"""
        settings = DashboardSettings.objects.create(
            user=user,
            layout_columns=4,
            theme='light',
            visible_widgets=[1, 2, 3, 4, 5, 6, 7, 8],  # All widgets visible by default
            hidden_widgets=[],
            auto_refresh=True,
            refresh_interval=300,
            email_alerts=True,
            browser_notifications=True,
            default_date_range='last_30_days'
        )

        return [settings]