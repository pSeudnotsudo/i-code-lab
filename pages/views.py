from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from .tokens import email_confirmation_token
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()

EYE_SVG = """<svg width="18" height="18" fill="none" stroke="currentColor"
  stroke-width="1.8" viewBox="0 0 24 24">
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/>
  <circle cx="12" cy="12" r="3"/>
</svg>"""


def _redirect_by_role(user):
    """Return the correct redirect for a logged-in user based on their role."""
    if user.is_superuser or user.role == User.ADMIN:
        return redirect('admin_dashboard')
    if user.role == User.PARENT:
        return redirect('parent_dashboard')
    return redirect('index')


# ─── LOGIN ───────────────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return render(request, 'authentication/auth_page.html', {'active_tab': 'login'})

        if not user.is_superuser and not user.is_email_verified:
            messages.error(request, "Please confirm your email before logging in.")
            return render(request, 'authentication/auth_page.html', {'active_tab': 'login'})

        auth_login(request, user)
        return _redirect_by_role(user)

    return render(request, 'authentication/auth_page.html', {'active_tab': 'login'})




def register(request):
    if request.method == 'POST':
        email     = request.POST.get('email', '').strip().lower()
        username  = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role      = request.POST.get('role', 'student')

        # Block anyone trying to register as admin via POST manipulation
        if role not in ('student', 'parent'):
            role = 'student'

        # ── Validation ──────────────────────────────────────
        error = None

        if not all([email, username, password1, password2]):
            error = "All fields are required."
        elif password1 != password2:
            error = "Passwords do not match."
        elif len(password1) < 8:
            error = "Password must be at least 8 characters."
        elif User.objects.filter(email=email).exists():
            error = "An account with this email already exists."
        elif User.objects.filter(username=username).exists():
            error = "This username is already taken."

        if error:
            messages.error(request, error)
            return render(request, 'authentication/auth_page.html', {'active_tab': 'register'})

         # ── Create inactive user ─────────────────────────────
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=False,
            is_email_verified=False,
        )

        # ---------------- Send confirmation email ──────────────────────────
        uid         = urlsafe_base64_encode(force_bytes(user.pk))
        token       = email_confirmation_token.make_token(user)
        confirm_url = f"http://{settings.SITE_DOMAIN}/auth/confirm-email/{uid}/{token}/"

        html_message = render_to_string('emails/confirm_email.html', {
            'username':    user.username,
            'first_name':  user.first_name,
            'last_name':   user.last_name, 
            'role':        role,
            'confirm_url': confirm_url,
        })

        send_mail(
            subject="Confirm your I-Code email address",
            message=strip_tags(html_message),   
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return redirect('email_confirm_sent')

    return redirect('login')


def confirm_email(request, uidb64, token):
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None
        
     # Already confirmed — just send them to login
    if user and user.is_email_verified:
        messages.info(request, "Your email is already confirmed. Please log in.")
        return redirect('login')

    if user and email_confirmation_token.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        return render(request, 'authentication/email_confirm_success.html')

    return render(request, 'authentication/email_confirm_failed.html')


@login_required
def parent_dashboard(request):
    if request.user.is_authenticated:
        current_username = request.user.username
    return render(request, 'dashboards/parent.html', {'current_username':current_username})

def logout_view(request):
    logout(request)
    return redirect('index')


def index(request):
    return render(request, 'index.html')


def programs(request):
    return render(request, 'programs.html')


def about(request):
    return render(request, 'about.html')


def pricing(request):
    return render(request, 'membership.html')
