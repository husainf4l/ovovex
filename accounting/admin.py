from django.contrib import admin
from .models import (
    Account,
    JournalEntry,
    JournalEntryLine,
    Customer,
    Invoice,
    InvoiceLine,
    Payment,
    UserProfile,
    Vendor,
    Bill,
    BillLine,
    Budget,
    BudgetLine,
    FixedAsset,
    ExpenseCategory,
    Expense,
    TaxRate,
    TaxReturn,
    AssetTaxInfo,
    BankStatement,
    BankReconciliation,
    ReconciliationAdjustment,
    AIInsight,
    AIPrediction,
    AIModel,
    AnomalyAlert,
    AnomalyDetectionModel,
    Notification,
    DocumentCategory,
    Document,
    DocumentShare,
    PurchaseOrder,
    PurchaseOrderLine,
    AuditTrail,
    ComplianceCheck,
    ComplianceViolation,
    InventoryCategory,
    InventoryItem,
    InventoryTransaction,
    DashboardKPIMetric,
    DashboardWidget,
    DashboardChartData,
    DashboardAlert,
    DashboardActivity,
    DashboardSettings,
    PricingPlan,
    Subscription,
    PaymentMethod,
    BillingHistory,
)


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2
    fields = ["account", "description", "debit_amount", "credit_amount"]


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1
    fields = ["description", "quantity", "unit_price", "line_total"]


class BillLineInline(admin.TabularInline):
    model = BillLine
    extra = 1
    fields = ["description", "quantity", "unit_price", "line_total"]


class BudgetLineInline(admin.TabularInline):
    model = BudgetLine
    extra = 1
    fields = ["account", "budgeted_amount", "actual_amount", "variance"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "account_type", "balance", "is_active"]
    list_filter = ["account_type", "is_active"]
    search_fields = ["code", "name", "description"]
    ordering = ["code"]


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = [
        "entry_number",
        "entry_date",
        "description",
        "total_debit",
        "total_credit",
        "status",
        "is_balanced",
    ]
    list_filter = ["status", "entry_date"]
    search_fields = ["entry_number", "description", "reference"]
    inlines = [JournalEntryLineInline]
    readonly_fields = ["total_debit", "total_credit", "created_at", "updated_at"]

    def is_balanced(self, obj):
        return obj.is_balanced()

    is_balanced.boolean = True


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "customer_code",
        "company_name",
        "contact_name",
        "email",
        "company",
        "is_active",
    ]
    list_filter = ["is_active", "company"]
    search_fields = ["customer_code", "company_name", "contact_name", "email"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "customer",
        "invoice_date",
        "due_date",
        "total_amount",
        "status",
    ]
    list_filter = ["status", "invoice_date"]
    search_fields = ["invoice_number", "customer__company_name"]
    inlines = [InvoiceLineInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "payment_number",
        "customer",
        "payment_date",
        "amount",
        "payment_method",
    ]
    list_filter = ["payment_method", "payment_date"]
    search_fields = ["payment_number", "customer__company_name"]


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ["vendor_code", "company_name", "contact_name", "email", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["vendor_code", "company_name", "contact_name", "email"]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = [
        "bill_number",
        "vendor",
        "bill_date",
        "due_date",
        "total_amount",
        "status",
    ]
    list_filter = ["status", "bill_date"]
    search_fields = ["bill_number", "vendor__company_name"]
    inlines = [BillLineInline]


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "fiscal_year",
        "period",
        "start_date",
        "end_date",
        "total_budget",
        "is_active",
    ]
    list_filter = ["fiscal_year", "period", "is_active"]
    search_fields = ["name"]
    inlines = [BudgetLineInline]


@admin.register(FixedAsset)
class FixedAssetAdmin(admin.ModelAdmin):
    list_display = [
        "asset_code",
        "name",
        "purchase_date",
        "purchase_cost",
        "book_value",
        "is_active",
    ]
    list_filter = ["is_active", "depreciation_method"]
    search_fields = ["asset_code", "name"]


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "account", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["expense_number", "category", "expense_date", "amount", "status"]
    list_filter = ["status", "category", "expense_date"]
    search_fields = ["expense_number", "description"]


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ["name", "rate", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(TaxReturn)
class TaxReturnAdmin(admin.ModelAdmin):
    list_display = [
        "return_number",
        "tax_period_start",
        "tax_period_end",
        "filing_date",
        "total_tax",
        "status",
    ]
    list_filter = ["status"]
    search_fields = ["return_number"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "company", "phone", "job_title"]
    search_fields = ["user__username", "user__email", "company"]
    list_filter = ["created_at"]


@admin.register(AssetTaxInfo)
class AssetTaxInfoAdmin(admin.ModelAdmin):
    list_display = [
        "asset",
        "tax_depreciation_method",
        "property_class",
        "tax_basis",
        "tax_book_value",
    ]
    list_filter = ["tax_depreciation_method", "property_class"]
    search_fields = ["asset__asset_code", "asset__name"]


@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_id",
        "account",
        "statement_date",
        "amount",
        "statement_type",
        "is_reconciled",
    ]
    list_filter = ["statement_type", "is_reconciled", "statement_date"]
    search_fields = ["transaction_id", "description", "reference_number"]


@admin.register(BankReconciliation)
class BankReconciliationAdmin(admin.ModelAdmin):
    list_display = [
        "account",
        "reconciliation_date",
        "statement_balance",
        "book_balance",
        "status",
    ]
    list_filter = ["status", "reconciliation_date"]
    search_fields = ["account__code", "account__name"]


@admin.register(ReconciliationAdjustment)
class ReconciliationAdjustmentAdmin(admin.ModelAdmin):
    list_display = [
        "reconciliation",
        "adjustment_type",
        "description",
        "amount",
        "is_addition",
    ]
    list_filter = ["adjustment_type", "is_addition"]
    search_fields = ["description"]


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = [
        "insight_id",
        "title",
        "insight_type",
        "priority",
        "confidence_score",
        "is_active",
    ]
    list_filter = ["insight_type", "priority", "is_active"]
    search_fields = ["insight_id", "title", "description"]


@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = [
        "prediction_id",
        "title",
        "prediction_type",
        "predicted_value",
        "prediction_date",
    ]
    list_filter = ["prediction_type", "prediction_date"]
    search_fields = ["prediction_id", "title"]


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ["model_name", "model_type", "version", "status", "accuracy_score"]
    list_filter = ["model_type", "status"]
    search_fields = ["model_name"]


@admin.register(AnomalyAlert)
class AnomalyAlertAdmin(admin.ModelAdmin):
    list_display = [
        "alert_id",
        "title",
        "anomaly_type",
        "severity",
        "status",
        "detected_at",
    ]
    list_filter = ["anomaly_type", "severity", "status"]
    search_fields = ["alert_id", "title", "description"]


@admin.register(AnomalyDetectionModel)
class AnomalyDetectionModelAdmin(admin.ModelAdmin):
    list_display = [
        "model_name",
        "model_type",
        "version",
        "is_active",
        "total_alerts_generated",
    ]
    list_filter = ["model_type", "is_active"]
    search_fields = ["model_name"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "notification_type", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["user__username", "title", "message"]


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent_category", "is_active", "color_code"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "document_id",
        "title",
        "document_type",
        "status",
        "uploaded_by",
        "uploaded_at",
    ]
    list_filter = ["document_type", "status", "is_confidential"]
    search_fields = ["document_id", "title", "description"]


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ["document", "shared_with", "access_level", "shared_by", "shared_at"]
    list_filter = ["access_level", "shared_at"]
    search_fields = ["document__title", "shared_with__username"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["po_number", "vendor", "order_date", "total_amount", "status"]
    list_filter = ["status", "order_date"]
    search_fields = ["po_number", "vendor__company_name"]


@admin.register(PurchaseOrderLine)
class PurchaseOrderLineAdmin(admin.ModelAdmin):
    list_display = [
        "purchase_order",
        "item_description",
        "quantity_ordered",
        "quantity_received",
        "unit_price",
    ]
    search_fields = ["item_description", "purchase_order__po_number"]


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "action_type",
        "entity_type",
        "entity_name",
        "timestamp",
        "success",
    ]
    list_filter = ["action_type", "entity_type", "success", "timestamp"]
    search_fields = ["user__username", "entity_name", "entity_id"]
    readonly_fields = [
        "user",
        "action_type",
        "entity_type",
        "entity_id",
        "timestamp",
        "old_values",
        "new_values",
    ]


@admin.register(ComplianceCheck)
class ComplianceCheckAdmin(admin.ModelAdmin):
    list_display = [
        "check_id",
        "title",
        "compliance_type",
        "status",
        "risk_level",
        "due_date",
    ]
    list_filter = ["compliance_type", "status", "risk_level"]
    search_fields = ["check_id", "title", "description"]


@admin.register(ComplianceViolation)
class ComplianceViolationAdmin(admin.ModelAdmin):
    list_display = ["violation_id", "title", "severity", "status", "detected_at"]
    list_filter = ["severity", "status"]
    search_fields = ["violation_id", "title", "description"]


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent_category", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = [
        "item_code",
        "name",
        "category",
        "current_stock",
        "unit_cost",
        "is_active",
    ]
    list_filter = ["category", "is_active"]
    search_fields = ["item_code", "name", "barcode"]


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ["item", "transaction_type", "quantity", "created_at"]
    list_filter = ["transaction_type", "created_at"]
    search_fields = ["item__item_code", "item__name"]


@admin.register(DashboardKPIMetric)
class DashboardKPIMetricAdmin(admin.ModelAdmin):
    list_display = ["name", "display_name", "metric_type", "current_value", "is_active"]
    list_filter = ["metric_type", "is_active"]
    search_fields = ["name", "display_name"]


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ["title", "widget_type", "is_active", "position_x", "position_y"]
    list_filter = ["widget_type", "is_active"]
    search_fields = ["title"]


@admin.register(DashboardChartData)
class DashboardChartDataAdmin(admin.ModelAdmin):
    list_display = ["widget", "label", "value", "date"]
    list_filter = ["widget", "date"]
    search_fields = ["label"]


@admin.register(DashboardAlert)
class DashboardAlertAdmin(admin.ModelAdmin):
    list_display = ["alert_type", "priority", "title", "is_read", "created_at"]
    list_filter = ["alert_type", "priority", "is_read"]
    search_fields = ["title", "message"]


@admin.register(DashboardActivity)
class DashboardActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "activity_type", "title", "created_at"]
    list_filter = ["activity_type", "created_at"]
    search_fields = ["user__username", "title", "description"]


@admin.register(DashboardSettings)
class DashboardSettingsAdmin(admin.ModelAdmin):
    list_display = ["user", "theme", "auto_refresh", "default_date_range"]
    list_filter = ["theme", "auto_refresh"]
    search_fields = ["user__username"]


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "plan_type", "price_monthly", "price_yearly", "is_active"]
    list_filter = ["plan_type", "is_active"]
    search_fields = ["name", "display_name"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "plan",
        "status",
        "current_period_start",
        "current_period_end",
        "billing_cycle",
    ]
    list_filter = ["status", "billing_cycle", "plan"]
    search_fields = ["user__username"]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["user", "payment_type", "is_default", "created_at"]
    list_filter = ["payment_type", "is_default"]
    search_fields = ["user__username", "card_last4"]


@admin.register(BillingHistory)
class BillingHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "subscription",
        "invoice_number",
        "amount",
        "status",
        "billing_period_start",
    ]
    list_filter = ["status", "billing_period_start"]
    search_fields = ["invoice_number", "subscription__user__username"]
