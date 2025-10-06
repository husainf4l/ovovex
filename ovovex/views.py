from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home(request):
    """
    Home page view
    """
    context = {
        'title': 'Welcome to Ovovex',
        'description': 'Your next-generation platform for innovative solutions.',
    }
    return render(request, 'home.html', context)

def health_check(request):
    """
    Simple health check endpoint
    """
    return HttpResponse("OK", content_type="text/plain")

def login_view(request):
    """
    Login page view
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {
        'title': 'Login to Ovovex',
        'description': 'Access your accounting dashboard and manage your finances.',
    }
    return render(request, 'auth/login.html', context)

def signup_view(request):
    """
    Signup page view
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if not all([username, email, first_name, last_name, password, password_confirm]):
            messages.error(request, 'Please fill in all fields.')
        elif password != password_confirm:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                messages.success(request, 'Account created successfully! You can now login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'An error occurred while creating your account.')
    
    context = {
        'title': 'Join Ovovex',
        'description': 'Create your account and start managing your finances today.',
    }
    return render(request, 'auth/signup.html', context)

def logout_view(request):
    """
    Logout view
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard_view(request):
    """
    Dashboard view for authenticated users
    """
    context = {
        'title': 'Dashboard',
        'description': 'Your accounting dashboard and financial overview.',
        'user': request.user,
    }
    return render(request, 'dashboard/dashboard.html', context)