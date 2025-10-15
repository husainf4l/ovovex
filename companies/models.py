from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    # Basic Information
    name = models.CharField(max_length=255, help_text="Company trading name")
    legal_name = models.CharField(max_length=255, blank=True, null=True, help_text="Legal/registered name")
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    industry_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Contact Information
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Registration & Tax
    registration_number = models.CharField(max_length=100, blank=True, null=True, help_text="Business registration number")
    tax_number = models.CharField(max_length=100, blank=True, null=True, help_text="Tax/VAT identification number")

    # Financial Settings
    currency = models.CharField(max_length=10, default="JOD")
    fiscal_year_start = models.DateField(blank=True, null=True, help_text="Start of fiscal year (e.g., Jan 1)")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_display_name(self):
        """Returns legal name if available, otherwise trading name"""
        return self.legal_name or self.name


class UserCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'company')
        verbose_name = "User Company"
        verbose_name_plural = "User Companies"

    def __str__(self):
        return f"{self.user.username} - {self.company.name} ({'Active' if self.is_active else 'Inactive'})"
