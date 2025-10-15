from django.contrib import admin
from .models import Company, UserCompany


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'industry_type', 'city', 'country', 'currency', 'created_at')
    search_fields = ('name', 'legal_name', 'tax_number', 'registration_number', 'email', 'city', 'country')
    list_filter = ('country', 'currency', 'industry_type', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'legal_name', 'logo', 'industry_type', 'description')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'country', 'phone', 'email', 'website')
        }),
        ('Registration & Tax', {
            'fields': ('registration_number', 'tax_number')
        }),
        ('Financial Settings', {
            'fields': ('currency', 'fiscal_year_start')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserCompany)
class UserCompanyAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'is_active')
    list_filter = ('is_active', 'company')
    search_fields = ('user__username', 'company__name')
    raw_id_fields = ('user', 'company')
