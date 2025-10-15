from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Company, UserCompany
import os


@login_required
def add_company(request):
    if request.method == "POST":
        name = request.POST.get("name")
        tax_number = request.POST.get("tax_number")
        address = request.POST.get("address")
        country = request.POST.get("country")

        # Create the company
        company = Company.objects.create(
            name=name,
            tax_number=tax_number,
            address=address,
            country=country
        )

        # Deactivate all other companies for this user
        UserCompany.objects.filter(user=request.user).update(is_active=False)

        # Create UserCompany link and set as active
        UserCompany.objects.create(user=request.user, company=company, is_active=True)

        messages.success(request, f"Company '{name}' created successfully!")
        return redirect("dashboard:dashboard")

    return render(request, "companies/add_company.html")


@login_required
def switch_company(request, company_id):
    # Deactivate all companies for this user
    UserCompany.objects.filter(user=request.user).update(is_active=False)

    # Activate the selected company
    user_company = UserCompany.objects.filter(user=request.user, company_id=company_id).first()

    if user_company:
        user_company.is_active = True
        user_company.save()
        messages.success(request, f"Switched to {user_company.company.name}")
    else:
        messages.error(request, "Company not found or you don't have access to it.")

    return redirect("dashboard:dashboard")


@login_required
def company_details(request):
    """View and edit company details"""
    active_company = request.active_company

    if not active_company:
        messages.warning(request, "Please select or create a company first.")
        return redirect("add_company")

    # Check if user has access to this company
    user_company = UserCompany.objects.filter(user=request.user, company=active_company).first()
    if not user_company:
        messages.error(request, "You don't have access to this company.")
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        # Update company details
        active_company.name = request.POST.get("name", active_company.name)
        active_company.legal_name = request.POST.get("legal_name", "")
        active_company.industry_type = request.POST.get("industry_type", "")
        active_company.description = request.POST.get("description", "")
        active_company.address = request.POST.get("address", "")
        active_company.city = request.POST.get("city", "")
        active_company.country = request.POST.get("country", "")
        active_company.phone = request.POST.get("phone", "")
        active_company.email = request.POST.get("email", "")
        active_company.website = request.POST.get("website", "")
        active_company.registration_number = request.POST.get("registration_number", "")
        active_company.tax_number = request.POST.get("tax_number", "")
        active_company.currency = request.POST.get("currency", "JOD")

        # Handle fiscal year start
        fiscal_year_start = request.POST.get("fiscal_year_start", "")
        if fiscal_year_start:
            active_company.fiscal_year_start = fiscal_year_start

        # Handle logo upload
        if request.FILES.get("logo"):
            # Delete old logo if exists
            if active_company.logo:
                if os.path.isfile(active_company.logo.path):
                    os.remove(active_company.logo.path)
            active_company.logo = request.FILES["logo"]

        active_company.save()
        messages.success(request, f"Company details updated successfully!")
        return redirect("company_details")

    context = {
        "company": active_company,
    }
    return render(request, "companies/company_details.html", context)


@login_required
def upload_logo(request):
    """AJAX endpoint for logo upload"""
    if request.method == "POST" and request.FILES.get("logo"):
        active_company = request.active_company

        if not active_company:
            return JsonResponse({"success": False, "error": "No active company"}, status=400)

        # Validate file
        logo = request.FILES["logo"]
        if logo.size > 2 * 1024 * 1024:  # 2MB limit
            return JsonResponse({"success": False, "error": "File size must be less than 2MB"}, status=400)

        if not logo.content_type in ["image/jpeg", "image/png", "image/jpg"]:
            return JsonResponse({"success": False, "error": "Only JPG and PNG files are allowed"}, status=400)

        # Delete old logo
        if active_company.logo:
            if os.path.isfile(active_company.logo.path):
                os.remove(active_company.logo.path)

        # Save new logo
        active_company.logo = logo
        active_company.save()

        return JsonResponse({
            "success": True,
            "logo_url": active_company.logo.url if active_company.logo else None
        })

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
def select_company(request):
    """Company selection page for users with multiple companies"""
    user_companies = UserCompany.objects.filter(user=request.user).select_related('company')

    # If user has only one company, activate it automatically
    if user_companies.count() == 1:
        uc = user_companies.first()
        uc.is_active = True
        uc.save()
        request.session['active_company_id'] = uc.company.id
        messages.success(request, f"Switched to {uc.company.name}")
        return redirect('dashboard:dashboard')

    # If user has no companies, redirect to create one
    if user_companies.count() == 0:
        messages.info(request, "Let's create your first company!")
        return redirect('add_company')

    context = {
        'user_companies': user_companies,
    }
    return render(request, 'companies/select_company.html', context)


@login_required
def select_and_activate_company(request, company_id):
    """Activate a specific company and redirect to dashboard"""
    # Verify user has access to this company
    user_company = UserCompany.objects.filter(
        user=request.user,
        company_id=company_id
    ).first()

    if not user_company:
        messages.error(request, "You don't have access to this company.")
        return redirect('select_company')

    # Deactivate all companies for this user
    UserCompany.objects.filter(user=request.user).update(is_active=False)

    # Activate selected company
    user_company.is_active = True
    user_company.save()

    # Store in session
    request.session['active_company_id'] = company_id

    messages.success(request, f"Switched to {user_company.company.name}")
    return redirect('dashboard:dashboard')
