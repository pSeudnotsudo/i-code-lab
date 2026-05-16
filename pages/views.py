from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied
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
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


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
        email    = request.POST.get('username', '').strip()  # field name stays 'username' in form
        password = request.POST.get('password', '')

        # look up user by email first
        try:
            user_obj = CustomUser.objects.get(email=email)
            user     = authenticate(request, username=user_obj.username, password=password)
        except CustomUser.DoesNotExist:
            user = None

        if user is None:
            messages.error(request, "Invalid email or password.")
            return render(request, 'authentication/auth_page.html', {'active_tab': 'login'})

        if not user.is_superuser and not user.is_email_verified:
            messages.error(request, "Your account is not activated yet. Check your email for the invite link.")
            return render(request, 'authentication/auth_page.html', {'active_tab': 'login'})

        auth_login(request, user)
        return _redirect_by_role(user)

    return render(request, 'authentication/auth_page.html', {'active_tab': 'login'})





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

# REDIRECT BY USER
def _redirect_by_role(user):
    if user.role == CustomUser.ADMIN or user.is_staff:
        return redirect('admin_dashboard')
    elif user.role == CustomUser.PARENT:
        return redirect('parent_dashboard')
    else:
        return redirect('student_dashboard')


# CREATE USER BY ADMIN 
@staff_member_required
def create_user(request):
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        role       = request.POST.get('role', 'student').strip()
        phone      = request.POST.get('phone', '').strip()

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return redirect('create_user')

        user = CustomUser.objects.create(
            username   = email,
            email      = email,
            first_name = first_name,
            last_name  = last_name,
            role       = role,
            phone      = phone,
            is_active  = False,
        )
        user.set_unusable_password()
        user.save()

        invite_link  = f"{settings.SITE_URL}/activate/{user.invite_token}/"
        html_content = render_to_string('emails/invite_email.html', {
            'first_name' : first_name,
            'last_name'  : last_name,
            'role'       : role,
            'invite_link': invite_link,
        })

        email_msg = EmailMultiAlternatives(
            subject    = 'Your I-Code AI Lab Account Invitation',
            body       = f'Hi {first_name}, set your password here: {invite_link}',
            from_email = settings.DEFAULT_FROM_EMAIL,
            to         = [email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        messages.success(request, f'Account created and invite sent to {email}.')
        return redirect('create_user')

    return render(request, 'icode-admin/create_user.html')



# 
#  USER ACCOUNTS
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
def activate_account(request, token):
    user = get_object_or_404(CustomUser, invite_token=token)

    if user.invite_token_used:
        return render(request, 'invite_invalid.html', {
            'message': 'This link has already been used.'
        })

    if request.method == 'POST':
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not password1:
            messages.error(request, 'Password cannot be empty.')
            return redirect('activate_account', token=token)

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('activate_account', token=token)

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('activate_account', token=token)

        user.set_password(password1)
        user.is_active         = True
        user.is_email_verified = True
        user.invite_token_used = True
        user.save()

        login(request, user)
        messages.success(request, f'Welcome {user.first_name}! Your account is active.')
        return _redirect_by_role(user)  

    return render(request, 'activate_account.html', {'user': user})





@login_required
def parent_dashboard(request):
    if request.user.is_authenticated:
        current_username = request.user.username
    return render(request, 'dashboards/parent.html', {'current_username':current_username})

@login_required
def student_dashboard(request):
    if request.user.is_authenticated:
        current_username = request.user.username
    return render(request, 'dashboards/student.html', {'current_username':current_username})

def logout_view(request):
    logout(request)
    return redirect('index')


def index(request):
    brackets = AgeBracket.objects.all().order_by("order")
    programs = Program.objects.all()
    timelines = RegistrationTimeline.objects.all()
    return render(request, 'index.html', {'brackets': brackets, 'programs':programs, 'timelines':timelines})


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
@staff_member_required(login_url='/login/')
def gallery_upload(request):
    if not request.user.is_staff:
        raise PermissionDenied
    
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
@staff_member_required(login_url='/login/')
def icode_admin(request):
    if not request.user.is_staff:
        raise PermissionDenied
    
    today = timezone.now().date()
    last_month = today - timedelta(days=30)

    total = Enrollment.objects.count()
    last_month_total = Enrollment.objects.filter(created_at__date__lt=last_month).count()
    growth = round(((total - last_month_total) / last_month_total * 100) if last_month_total else 0)

    pending_status = EnrollmentStatus.objects.filter(code='pending').first()
    confirmed_status = EnrollmentStatus.objects.filter(code='confirmed').first()
    pending_count = Enrollment.objects.filter(status=pending_status).count() if pending_status else 0
    confirmed_count = Enrollment.objects.filter(status=confirmed_status).count() if confirmed_status else 0
    conversion_rate = round((confirmed_count / total * 100) if total else 0)

    program_colors = ['#49BBBD','#9B59B6','#F48C06','#3DA4A6','#5D6C7B','#1a7a4a']
    prog_qs = (Program.objects.filter(is_active=True)
               .annotate(count=Count('enrollment'))
               .order_by('-count')[:6])
    
    max_count = max((p.count for p in prog_qs), default=0) or 1
    program_stats = [
        {'name': p.name, 'count': p.count,
         'pct': round(p.count / max_count * 100),
         'color': program_colors[i % len(program_colors)]}
        for i, p in enumerate(prog_qs)
    ]

    week_labels, week_data = [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        week_labels.append(day.strftime('%a'))
        week_data.append(Enrollment.objects.filter(created_at__date=day).count())

   
    month_labels, month_data = [], []
    for i in range(11, -1, -1):
        d = today.replace(day=1) - timedelta(days=i*28)
        month_labels.append(d.strftime('%b'))
        month_data.append(Enrollment.objects.filter(
            created_at__year=d.year, created_at__month=d.month).count())

    return render(request, 'icode-admin/admin_dash.html', {
        'total_enrollments': total,
        'enrollment_growth': growth,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'conversion_rate': conversion_rate,
        'active_programs': Program.objects.filter(is_active=True).count(),
        'age_brackets': AgeBracket.objects.filter(is_active=True).count(),
        'program_stats': program_stats,
        'recent_enrollments': Enrollment.objects.select_related('status').prefetch_related('programs').order_by('-created_at')[:8],
        'week_labels': json.dumps(week_labels),
        'week_data': json.dumps(week_data),
        'month_labels': json.dumps(month_labels),
        'month_data': json.dumps(month_data),
        'new_today': Enrollment.objects.filter(created_at__date=today).count(),
    })
    



@staff_member_required(login_url='/login/')
def icode_enrollments(request):
    if not request.user.is_staff:
        raise PermissionDenied
    status_filter = request.GET.get("status", "").strip().lower()
 
    enrollments = Enrollment.objects.select_related(
        "status", "age_bracket", "registration_timeline"
    ).prefetch_related("programs").order_by("-created_at")
 
    if status_filter:
        enrollments = enrollments.filter(status__code=status_filter)
 
    
    all_enrollments = Enrollment.objects.select_related("status")
    total_count     = all_enrollments.count()
    pending_count   = all_enrollments.filter(status__code="pending").count()
    confirmed_count = all_enrollments.filter(status__code="confirmed").count()
    rejected_count  = all_enrollments.filter(status__code="rejected").count()
 
    return render(request, "icode-admin/enrollment_list.html", {
        "enrollments":      enrollments,
        "current_status":   status_filter,
        "total_count":      total_count,
        "pending_count":    pending_count,
        "confirmed_count":  confirmed_count,
        "rejected_count":   rejected_count,
    })
 
 
#  APPROVE ENROLLMENTS
@staff_member_required(login_url='/login/')
def enrollment_update_status(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    
    """
    POST-only view.
    Expects: action = "approve" | "reject"
    Uses a DB transaction so the status update and email are atomic.
    (email is sent after commit to avoid holding the transaction open)
    """
    if request.method != "POST":
        return redirect("icode_enrollments")
 
    action     = request.POST.get("action", "").strip().lower()
    enrollment = get_object_or_404(Enrollment, pk=pk)
 
    if action not in ("approve", "reject"):
        messages.error(request, "Invalid action.")
        return redirect("icode_enrollments")
 
    # Map action → status code
    target_code = "confirmed" if action == "approve" else "rejected"
 
    # Fetch target status
    target_status = EnrollmentStatus.objects.filter(code=target_code).first()
    if not target_status:
        messages.error(
            request,
            f"System error: EnrollmentStatus with code='{target_code}' not found."
        )
        return redirect("icode_enrollments")
 
    # Prevent double-processing
    if enrollment.status.code == target_code:
        messages.warning(
            request,
            f"{enrollment.full_name}'s enrollment is already {target_code}."
        )
        return redirect("icode_enrollments")
 
    # ── Atomic update ────────────────────────────────────────────────────────
    try:
        with transaction.atomic():
            enrollment.status = target_status
            enrollment.save(update_fields=["status"])
 
        # Email sent AFTER commit (keeps transaction short)
        _send_status_email(enrollment, action)
 
        label = "approved" if action == "approve" else "rejected"
        messages.success(
            request,
            f"Enrollment for {enrollment.full_name} has been {label}. "
            f"An email has been sent to {enrollment.email}."
        )
 
    except Exception as e:
        messages.error(request, f"Something went wrong: {str(e)}")
 
    return redirect("icode_enrollments")

#  HELPER FUNCTION TO SEND EMAILS

def _send_status_email(enrollment, action):
    if action == "approve":
        subject = "Enrollment Confirmed — i-Code"
        message = (
            f"Dear {enrollment.full_name},\n\n"
            "Great news! Your enrollment has been reviewed and confirmed.\n\n"
            "Our team will be in touch shortly with the next steps and class details.\n\n"
            "We look forward to having you at i-Code!\n\n"
            "Warm regards,\n"
            "The i-Code Team"
        )
    else:
        subject = "Enrollment Update — i-Code"
        message = (
            f"Dear {enrollment.full_name},\n\n"
            "Thank you for your interest in i-Code.\n\n"
            "After careful review, we regret to inform you that we are unable to "
            "proceed with your enrollment at this time.\n\n"
            "If you have any questions or would like to discuss alternative options, "
            "please don't hesitate to reach out to us.\n\n"
            "We appreciate your interest and hope to work with you in the future.\n\n"
            "Kind regards,\n"
            "The i-Code Team"
        )
 
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[enrollment.email],
        fail_silently=False,   # raise errors so the caller can catch them
    )

 # PROGRAMS


def programs_list(request):

    programs = Program.objects.all().order_by("order")

    context = {
        "programs": programs
    }

    return render(
        request,
        "icode-admin/program_list.html",
        context
    )


@require_POST
def program_store(request):

    try:

        data = json.loads(request.body)

        name = data.get("name")
        code = data.get("code")
        description = data.get("description")
        order = data.get("order", 0)

        if not name:

            return JsonResponse({
                "success": False,
                "error": "Program name is required"
            })

        if not code:

            return JsonResponse({
                "success": False,
                "error": "Program code is required"
            })

        if Program.objects.filter(code=code).exists():

            return JsonResponse({
                "success": False,
                "error": "Program code already exists"
            })

        program = Program.objects.create(
            name=name,
            code=code,
            description=description,
            order=order,
            is_active=True
        )

        return JsonResponse({

            "success": True,
            "message": "Program added successfully",

            "program": {
                "id": program.id,
                "name": program.name,
                "code": program.code,
                "description": program.description or "",
                "order": program.order,
                "active": program.is_active
            }

        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        })


@require_POST
def program_update(request, pk):

    try:

        program = get_object_or_404(
            Program,
            pk=pk
        )

        data = json.loads(request.body)

        name = data.get("name")
        code = data.get("code")
        description = data.get("description")
        order = data.get("order", 0)
        is_active = data.get("is_active", True)

        if not name:

            return JsonResponse({
                "success": False,
                "error": "Program name is required"
            })

        if not code:

            return JsonResponse({
                "success": False,
                "error": "Program code is required"
            })

        exists = Program.objects.exclude(
            id=program.id
        ).filter(
            code=code
        ).exists()

        if exists:

            return JsonResponse({
                "success": False,
                "error": "Program code already exists"
            })

        program.name = name
        program.code = code
        program.description = description
        program.order = order
        program.is_active = is_active

        program.save()

        return JsonResponse({
            "success": True,
            "message": "Program updated successfully"
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        })




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
        
        

# REGISTRATION TIMELINES
def timeline_list(request):

    timelines = RegistrationTimeline.objects.all().order_by("order")

    return render(
        request,
        "icode-admin/timelines.html",
        {"timelines": timelines}
    )
    
@require_POST
def timeline_store(request):

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

        if RegistrationTimeline.objects.filter(code=code).exists():
            return JsonResponse({
                "success": False,
                "error": "Code already exists"
            })

        timeline = RegistrationTimeline.objects.create(
            title=title,
            code=code,
            order=order,
            is_active=True
        )

        return JsonResponse({
            "success": True,
            "message": "Timeline added successfully",
            "timeline": {
                "id": timeline.id,
                "title": timeline.title,
                "code": timeline.code,
                "order": timeline.order,
                "active": timeline.is_active
            }
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })


@require_POST
def timeline_update(request, pk):

    try:

        timeline = get_object_or_404(RegistrationTimeline, pk=pk)

        data = json.loads(request.body)

        title = data.get("title")
        code = data.get("code")
        order = data.get("order", 0)
        is_active = data.get("is_active", True)

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

        exists = RegistrationTimeline.objects.exclude(
            id=timeline.id
        ).filter(
            code=code
        ).exists()

        if exists:
            return JsonResponse({
                "success": False,
                "error": "Code already exists"
            })

        timeline.title = title
        timeline.code = code
        timeline.order = order
        timeline.is_active = is_active
        timeline.save()

        return JsonResponse({
            "success": True,
            "message": "Timeline updated successfully"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })



# ENROLLMENT
@csrf_exempt
def enrollment_store(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})
 
    # ── Core fields ──────────────────────────────────────────────────────────
    full_name   = request.POST.get("full_name", "").strip()
    phone       = request.POST.get("phone", "").strip()
    email       = request.POST.get("email", "").strip()
    comments    = request.POST.get("comments", "").strip()
    program_ids = request.POST.getlist("programs")
 
    # ── New fields ───────────────────────────────────────────────────────────
    age_bracket_id              = request.POST.get("age_bracket")
    preferred_registration_date = request.POST.get("preferred_registration_date")  
    registration_timeline_id    = request.POST.get("registration_timeline")
    prospective_start_date      = request.POST.get("preferred_start_date")       
    customized_course           = request.POST.get("customized_course", "no")      
 
    # ── Lookups ──────────────────────────────────────────────────────────────
    status = EnrollmentStatus.objects.filter(code="pending").first()
 
    age_bracket = None
    if age_bracket_id:
        age_bracket = AgeBracket.objects.filter(id=age_bracket_id, is_active=True).first()
    
    if not age_bracket:
        age_bracket = AgeBracket.objects.filter(is_active=True).first()
 
    registration_timeline = None
    if registration_timeline_id:
        registration_timeline = RegistrationTimeline.objects.filter(
            id=registration_timeline_id
        ).first()
 
    # ── Create enrollment ────────────────────────────────────────────────────
    enrollment = Enrollment.objects.create(
        full_name=full_name,
        phone=phone,
        email=email,
        comments=comments,
        status=status,
        age_bracket=age_bracket,
        preferred_registration_date=preferred_registration_date or None,
        registration_timeline=registration_timeline,
        preferred_start_date=prospective_start_date or None,
        # custom_course_interest=(customized_course == "yes"),
        custom_course_interest=customized_course if customized_course in ("yes", "no") else None,
    )
 
    # ── M2M programs ─────────────────────────────────────────────────────────
    if program_ids:
        enrollment.programs.set(Program.objects.filter(id__in=program_ids))
 
    # ── Email notification ───────────────────────────────────────────────────
    send_mail(
        subject="Enrollment Received - i-Code",
        message=(
            f"Hello {full_name},\n\n"
            "We have received your enrollment successfully.\n\n"
            "Our team will review your request and get back to you shortly.\n\n"
            "Thank you for choosing i-Code."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
 
    return JsonResponse({
        "success": True,
        "message": "Enrollment submitted successfully!"
    })
 
 
 
