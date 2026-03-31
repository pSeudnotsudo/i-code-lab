from django.shortcuts import get_object_or_404, render,redirect


def login(request):
    return render(request, 'authentication/auth_page.html',)

def register(request):
    return render(request, 'register.html',)

def index(request):
    return render(request, 'index.html',)

def courses(request):
    return render(request, 'courses.html',)

def about(request):
    return render(request, 'about.html',)

def services(request):
    return render(request, 'services.html',)

# Membership
def membership(request):
    return render(request, 'membership.html')


