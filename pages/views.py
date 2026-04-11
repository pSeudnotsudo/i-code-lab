from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'authentication/auth_page.html', {'active_tab': 'login'})


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password1')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'authentication/auth_page.html', {'active_tab': 'register'})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'authentication/auth_page.html', {'active_tab': 'register'})

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('index')

    return render(request, 'authentication/auth_page.html', {'active_tab': 'register'})


def index(request):
    return render(request, 'index.html')


def programs(request):
    return render(request, 'programs.html')


def about(request):
    return render(request, 'about.html')


def membership(request):
    return render(request, 'membership.html')
