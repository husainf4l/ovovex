from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import LoginForm, SignupForm
from companies.models import UserCompany


def login_view(request):
    """
    Login page view
    """
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, f"Welcome back, {user.first_name or user.username}!"
                )

                # Check user's companies and redirect accordingly
                user_companies = UserCompany.objects.filter(user=user)
                company_count = user_companies.count()

                if company_count == 0:
                    # No companies - redirect to create first company
                    messages.info(request, "Let's set up your first company!")
                    return redirect('add_company')
                elif company_count == 1:
                    # One company - auto-activate and go to dashboard
                    uc = user_companies.first()
                    uc.is_active = True
                    uc.save()
                    request.session['active_company_id'] = uc.company.id
                    return redirect('dashboard:dashboard')
                else:
                    # Multiple companies - let user choose
                    return redirect('select_company')

                # Fallback (shouldn't reach here)
                next_url = request.GET.get("next", "dashboard:dashboard")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()

    context = {
        "title": "Login to Ovovex",
        "description": "Access your accounting dashboard and manage your finances.",
        "form": form,
    }
    return render(request, "accounts/login.html", context)


def signup_view(request):
    """
    Signup page view
    """
    # Allow viewing signup pages even when authenticated (they might want to see the page)
    # Only redirect on POST (actual signup attempt)
    if request.user.is_authenticated and request.method == "POST":
        messages.info(request, "You are already logged in.")
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after account creation
            login(request, user)
            messages.success(
                request, f"Welcome to Ovovex, {user.first_name or user.username}! Your account has been created successfully."
            )
            # New users need to create their first company
            messages.info(request, "Let's create your first company to get started!")
            return redirect("add_company")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()

    context = {
        "title": "Join Ovovex",
        "description": "Create your account and start managing your finances today.",
        "form": form,
    }
    return render(request, "accounts/signup.html", context)


def logout_view(request):
    """
    Logout view - clears session including active company
    """
    # Clear active company session
    if 'active_company_id' in request.session:
        del request.session['active_company_id']

    logout(request)
    # messages.success(request, "You have been logged out successfully.")
    return redirect("home")
