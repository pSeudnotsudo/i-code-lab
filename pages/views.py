from django.shortcuts import render, redirect, get_object_or_404
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
from .models import *
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json


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

def socials(request):
    items = GalleryItem.objects.all()

    return render (request, 'socials.html',{'items': items})




# @login_required
def gallery_upload(request):
    if request.method == 'POST':
        # --- pull raw fields from request.POST / request.FILES ---
        title    = request.POST.get('title', '').strip()
        category = request.POST.get('category', '').strip()
        date     = request.POST.get('date', '').strip()
        caption  = request.POST.get('caption', '').strip()
        media    = request.FILES.get('media')

        # --- validation ---
        errors = {}
        if not title:
            errors['title'] = 'Title is required.'
        if category not in ('event', 'workshop', 'community'):
            errors['category'] = 'Select a valid category.'
        if not date:
            errors['date'] = 'Date is required.'
        if not media:
            errors['media'] = 'Please choose a file.'
        else:
            if media.size > 50 * 1024 * 1024:
                errors['media'] = 'File too large — maximum 50 MB.'
            else:
                allowed_images = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
                allowed_videos = {'.mp4', '.mov', '.webm', '.avi', '.mkv'}
                ext = os.path.splitext(media.name)[1].lower()
                if ext not in (allowed_images | allowed_videos):
                    errors['media'] = 'Unsupported file type.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # --- save ---
        ext = os.path.splitext(media.name)[1].lower()
        media_type = 'video' if ext in {'.mp4', '.mov', '.webm', '.avi', '.mkv'} else 'image'

        item = GalleryItem.objects.create(
            title    = title,
            media    = media,
            type     = media_type,
            category = category,
            date     = date,
            caption  = caption,
        )

        return JsonResponse({
            'success': True,
            'message': f'"{item.title}" uploaded successfully!',
            'item': {
                'id':       item.id,
                'title':    item.title,
                'type':     item.type,
                'category': item.category,
                'date':     str(item.date),
            }
        })

    recent_items = GalleryItem.objects.order_by('-uploaded_at')[:8]
    return render(request, 'gallery_upload.html', {'recent_items': recent_items})



# ADMIN LAYOUT AND EVERYTHING ADMIN
def icode_admin(request):
    items = GalleryItem.objects.all()
    # print(items)

    return render (request, 'icode-admin/admin_dash.html',{'items': items})


def icode_enrollments(request):
    enrollments = Enrollment.objects.all()

    return render (request, 'icode-admin/enrollment_list.html',{'enrollments': enrollments})
 
 
def icode_programs(request):
    programs = Program.objects.all()

    return render (request, 'icode-admin/enrollment_list.html',{'programs': programs})


# AGE BRACKETS
def age_brackets(request):

    brackets = AgeBracket.objects.all().order_by("order")

    context = {
        "brackets": brackets
    }

    return render(
        request,
        "icode-admin/age_brackets.html",
        context
    )
    

@require_POST
def age_bracket_store(request):

    try:

        data = json.loads(request.body)

        title = data.get("title")
        code = data.get("code")
        order = data.get("order", 0)

        if not title:
            return JsonResponse({
                "success": False,
                "error": "Title is required"
            })

        if not code:
            return JsonResponse({
                "success": False,
                "error": "Code is required"
            })

        if AgeBracket.objects.filter(code=code).exists():
            return JsonResponse({
                "success": False,
                "error": "Code already exists"
            })

        bracket = AgeBracket.objects.create(
            title=title,
            code=code,
            order=order,
            is_active=True
        )

        return JsonResponse({
            "success": True,
            "message": "Bracket added successfully",
            "bracket": {
                "id": bracket.id,
                "title": bracket.title,
                "code": bracket.code,
                "status": "Active"
            }
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        })


# Status List
def status_list(request):

    statuses = EnrollmentStatus.objects.all().order_by("order")

    context = {
        "statuses": statuses
    }

    return render(
        request,
        "icode-admin/enrollment_status.html",
        context
    )
    
@require_POST
def status_store(request):

    try:

        data = json.loads(request.body)

        name = data.get("name")
        code = data.get("code")
        order = data.get("order", 0)

        if not name:
            return JsonResponse({
                "success": False,
                "error": "Status name is required"
            })

        if not code:
            return JsonResponse({
                "success": False,
                "error": "Status code is required"
            })

        if EnrollmentStatus.objects.filter(code=code).exists():

            return JsonResponse({
                "success": False,
                "error": "Status code already exists"
            })

        status = EnrollmentStatus.objects.create(
            name=name,
            code=code,
            order=order,
            is_active=True
        )

        return JsonResponse({

            "success": True,
            "message": "Status added successfully",

            "status": {
                "id": status.id,
                "name": status.name,
                "code": status.code,
                "order": status.order,
                "active": status.is_active
            }

        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        })


@require_POST
def status_update(request, pk):

    try:

        status = get_object_or_404(
            EnrollmentStatus,
            pk=pk
        )

        data = json.loads(request.body)

        name = data.get("name")
        code = data.get("code")
        order = data.get("order", 0)
        is_active = data.get("is_active", True)

        if not name:

            return JsonResponse({
                "success": False,
                "error": "Status name is required"
            })

        if not code:

            return JsonResponse({
                "success": False,
                "error": "Status code is required"
            })

        exists = EnrollmentStatus.objects.exclude(
            id=status.id
        ).filter(
            code=code
        ).exists()

        if exists:

            return JsonResponse({
                "success": False,
                "error": "Status code already exists"
            })

        status.name = name
        status.code = code
        status.order = order
        status.is_active = is_active

        status.save()

        return JsonResponse({
            "success": True,
            "message": "Status updated successfully"
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        })
