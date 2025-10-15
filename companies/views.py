from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Company, UserCompany


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
