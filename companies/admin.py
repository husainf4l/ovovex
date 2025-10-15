from django.contrib import admin
from .models import Company, UserCompany


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_number', 'country', 'currency', 'created_at')
    search_fields = ('name', 'tax_number', 'country')
    list_filter = ('country', 'currency', 'created_at')


@admin.register(UserCompany)
class UserCompanyAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'is_active')
    list_filter = ('is_active', 'company')
    search_fields = ('user__username', 'company__name')
    raw_id_fields = ('user', 'company')
