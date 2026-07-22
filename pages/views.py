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
from django.views.decorators.http import require_POST,require_GET
import json
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import transaction
from django.http import FileResponse
from django.conf import settings
from django.contrib import messages



User = get_user_model()

EYE_SVG = """<svg width="18" height="18" fill="none" stroke="currentColor"
  stroke-width="1.8" viewBox="0 0 24 24">
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/>
  <circle cx="12" cy="12" r="3"/>
</svg>"""

def serve_privacy_policy(request):
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', 'privacy_policy.pdf')
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['X-Frame-Options'] = 'SAMEORIGIN'  
    return response
    

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
        email    = request.POST.get('username', '').strip()   
        password = request.POST.get('password', '')

        
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
        html_content = render_to_string('emails/invite_link.html', {
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
    testimonials = Testimonial.objects.filter(is_active=True)
    return render(request, 'index.html', {'brackets': brackets, 'programs':programs, 'timelines':timelines,"testimonials": testimonials})


def programs(request):
    brackets = AgeBracket.objects.all().order_by("order")
    programs = Program.objects.all()
    timelines = RegistrationTimeline.objects.all()
    return render(request, 'programs.html',{'brackets': brackets, 'programs':programs, 'timelines':timelines,})


def about(request):
    return render(request, 'about.html')


# def pricing(request):
#     return render(request, 'membership.html')
def team(request):
    featured = TeamMember.objects.filter(is_featured=True, is_active=True)
    members  = TeamMember.objects.filter(is_featured=False, is_active=True)
    age = AgeBracket.objects.all()
    courses_count = Program.objects.all()
    
    return render(request, 'membership.html', {
        'featured': featured,
        'members':members,
        'total':members.count(),
        'age_count':age.count(),
        'courses_count':courses_count.count()
    })

def socials(request):
    items = GalleryItem.objects.all()
    return render(request, 'socials.html', {
        'items':         items,
        'total_images':  items.filter(type='image').count(),
        'total_videos':  items.filter(type='video').count(),
        'total_events':  items.filter(category='event').count(),
    })




@login_required
@staff_member_required(login_url='/login/')
def gallery_upload(request):
    if not request.user.is_staff:
        raise PermissionDenied
    
    if request.method == 'POST':
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
 
    # enrollments = Enrollment.objects.select_related(
    #     "status", "age_bracket", "registration_timeline"
    # ).prefetch_related("programs").order_by("-created_at")
    
    enrollments = Enrollment.objects.select_related(
    "status", "age_bracket"
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
        return redirect("enrollments_list")
 
    action     = request.POST.get("action", "").strip().lower()
    enrollment = get_object_or_404(Enrollment, pk=pk)
 
    if action not in ("approve", "reject"):
        messages.error(request, "Invalid action.")
        return redirect("enrollments_list")
 
    target_code = "confirmed" if action == "approve" else "rejected"
 
    target_status = EnrollmentStatus.objects.filter(code=target_code, is_active='True').first()
    if not target_status:
        messages.error(
            request,
            f"System error: EnrollmentStatus with code='{target_code}' not found."
        )
        return redirect("enrollments_list")
 
   
    if enrollment.status.code == target_code:
        messages.warning(
            request,
            f"{enrollment.full_name}'s enrollment is already {target_code}."
        )
        return redirect("enrollments_list")
 
    # ── Atomic update ────────────────────────────────────────────────────────
    try:
        with transaction.atomic():
            enrollment.status = target_status
            enrollment.save(update_fields=["status"])
 
        _send_status_email(enrollment, action)
 
        label = "approved" if action == "approve" else "rejected"
        messages.success(
            request,
            f"Enrollment for {enrollment.full_name} has been {label}. "
            f"An email has been sent to {enrollment.email}."
        )
 
    except Exception as e:
        messages.error(request, f"Something went wrong: {str(e)}")
 
    return redirect("enrollments_list")


#  HELPER FUNCTION TO SEND EMAILS
def _send_status_email(enrollment, action):
    if action == "approve":
        subject  = "Enrollment Confirmed — i-Code"
        template = "emails/enrollment_confirmed.html"
    else:
        subject  = "Enrollment Update — i-Code"
        template = "emails/enrollment_rejected.html"

    programs_list = ", ".join(
        p.name for p in enrollment.programs.all()
    ) if hasattr(enrollment, "programs") else ""

    context = {
        "full_name": enrollment.full_name,
        "programs":  programs_list,
    }

    html_body  = render_to_string(template, context)
    plain_body = html_body  

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[enrollment.email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
    

# PROGRAMS
def programs_list(request):
    # programs = Program.objects.all().order_by("order")
    programs     = Program.objects.all().order_by("order")
    age_brackets = AgeBracket.objects.all()
    fees         = TermFee.objects.all()
    levels       = Level.objects.all().order_by("order")
    return render(
        request,
        "icode-admin/program_list.html",
        {
            "programs":     programs,
            "age_brackets": age_brackets,
            "fees":         fees,
            "levels":       levels,
        }
    )


def _parse_lines(value):
    """Convert a textarea blob (one item per line) to a clean list."""
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _decimal_or_none(value):
    try:
        from decimal import Decimal
        return Decimal(str(value))
    except (TypeError, ValueError):
        return None


@require_POST
def program_store(request):
    try:
        data = json.loads(request.body)

        name             = data.get("name", "").strip()
        code             = data.get("code", "").strip()
        description      = data.get("description", "").strip()
        hero_copy        = data.get("hero_copy", "").strip()
        fee_currency     = data.get("fee_currency", "KES").strip()
        certificate_name = data.get("certificate_name", "").strip()
        meta_description = data.get("meta_description", "").strip()
        order            = data.get("order", 0)

        duration_weeks    = _int_or_none(data.get("duration_weeks"))
        total_hours       = _int_or_none(data.get("total_hours"))
        what_they_build   = _parse_lines(data.get("what_they_build", ""))
        learning_outcomes = _parse_lines(data.get("learning_outcomes", ""))

        # FK ids
        level_id     = _int_or_none(data.get("level"))
        age_range_id = _int_or_none(data.get("age_range"))  # FIX: was age_range_id = age_range_id,
        term_fee     = _decimal_or_none(data.get("term_fee"))

        if not name:
            return JsonResponse({"success": False, "error": "Program name is required"})
        if not code:
            return JsonResponse({"success": False, "error": "Program code is required"})
        if Program.objects.filter(code=code).exists():
            return JsonResponse({"success": False, "error": "Program code already exists"})

        program = Program.objects.create(
            name              = name,
            code              = code,
            description       = description,
            hero_copy         = hero_copy,
            duration_weeks    = duration_weeks,
            total_hours       = total_hours,
            fee_currency      = fee_currency,
            certificate_name  = certificate_name,
            meta_description  = meta_description,
            what_they_build   = what_they_build,
            learning_outcomes = learning_outcomes,
            order             = order,
            is_active         = True,
            level_id          = level_id,
            age_range_id      = age_range_id,
            term_fee          = term_fee,
        )

        return JsonResponse({
            "success": True,
            "message": "Program added successfully",
            "program": {
                "id":               program.id,
                "name":             program.name,
                "code":             program.code,
                "description":      program.description or "",
                "hero_copy":        program.hero_copy or "",
                "age_range":        program.age_range_id or "",
                "level":            program.level_id or "",
                "duration_weeks":   program.duration_weeks,
                "total_hours":      program.total_hours,
                "term_fee":         str(program.term_fee) if program.term_fee else "",  # FIX
                "fee_currency":     program.fee_currency,
                "certificate_name": program.certificate_name,
                "meta_description": program.meta_description or "",
                "what_they_build":  "\n".join(program.what_they_build),
                "learning_outcomes":"\n".join(program.learning_outcomes),
                "order":            program.order,
                "is_active":        program.is_active,
            },
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def program_update(request, pk):
    try:
        program = get_object_or_404(Program, pk=pk)

        data = json.loads(request.body)

        name             = data.get("name", "").strip()
        code             = data.get("code", "").strip()
        description      = data.get("description", "").strip()
        hero_copy        = data.get("hero_copy", "").strip()
        fee_currency     = data.get("fee_currency", "KES").strip()
        certificate_name = data.get("certificate_name", "").strip()
        meta_description = data.get("meta_description", "").strip()
        order            = data.get("order", 0)
        is_active        = data.get("is_active", True)

        duration_weeks    = _int_or_none(data.get("duration_weeks"))
        total_hours       = _int_or_none(data.get("total_hours"))
        what_they_build   = _parse_lines(data.get("what_they_build", ""))
        learning_outcomes = _parse_lines(data.get("learning_outcomes", ""))

        # FK ids
        level_id     = _int_or_none(data.get("level"))
        age_range_id = _int_or_none(data.get("age_range"))
        term_fee     = _decimal_or_none(data.get("term_fee"))  # FIX: DecimalField, not FK

        if not name:
            return JsonResponse({"success": False, "error": "Program name is required"})
        if not code:
            return JsonResponse({"success": False, "error": "Program code is required"})
        if Program.objects.exclude(pk=program.pk).filter(code=code).exists():
            return JsonResponse({"success": False, "error": "Program code already exists"})

        program.name              = name
        program.code              = code
        program.description       = description
        program.hero_copy         = hero_copy
        program.duration_weeks    = duration_weeks
        program.total_hours       = total_hours
        program.fee_currency      = fee_currency
        program.certificate_name  = certificate_name
        program.meta_description  = meta_description
        program.what_they_build   = what_they_build
        program.learning_outcomes = learning_outcomes
        program.order             = order
        program.is_active         = is_active
        program.level_id          = level_id
        program.age_range_id      = age_range_id
        program.term_fee          = term_fee  # FIX: was program.term_fee_id
        program.save()

        return JsonResponse({"success": True, "message": "Program updated successfully"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
    
    
def program_detail(request, slug):
    program = get_object_or_404(Program, slug=slug, is_active=True)
    return render(request, 'program_detail.html', {'program': program})

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

    full_name       = request.POST.get("full_name", "").strip()
    phone           = request.POST.get("phone", "").strip()
    email           = request.POST.get("email", "").strip()
    comments        = request.POST.get("comments", "").strip()
    program_ids     = request.POST.getlist("programs")
    age_bracket_id  = request.POST.get("age_bracket")
    customized_course = request.POST.get("customized_course", "no")

    # ── New fields ───────────────────────────────────────────────────────
    referral_source = request.POST.get("referral_source", "").strip()
    track           = request.POST.get("track", "").strip()
    cohort_label    = request.POST.get("cohort_label", "").strip()
    # ─────────────────────────────────────────────────────────────────────

    # Default status → pending
    status = EnrollmentStatus.objects.filter(code="pending").first()

    # Age bracket
    age_bracket = None
    if age_bracket_id:
        age_bracket = AgeBracket.objects.filter(
            id=age_bracket_id, is_active=True
        ).first()
    if not age_bracket:
        age_bracket = AgeBracket.objects.filter(is_active=True).first()

    enrollment = Enrollment.objects.create(
        full_name             = full_name,
        phone                 = phone,
        email                 = email,
        comments              = comments,
        status                = status,
        age_bracket           = age_bracket,
        custom_course_interest = customized_course if customized_course in ("yes", "no") else None,
        referral_source       = referral_source,
        track                 = track,
        cohort_label          = cohort_label,
    )

    if program_ids:
        enrollment.programs.set(Program.objects.filter(id__in=program_ids))

    send_mail(
        subject="Enrollment Received — i-Code Robotics & AI Lab",
        message=(
            f"Hello {full_name},\n\n"
            "We have received your enrollment request successfully.\n\n"
            f"Cohort selected: {cohort_label}\n"
            f"Track: {track}\n\n"
            "Our team will review your request and get back to you within 24 hours.\n\n"
            "Thank you for choosing i-CODE Robotics & AI Lab.\n\n"
            "📍 Onestop Arcade, off Langata Road, Karen, Nairobi\n"
            "📞 +254 748 982 170 | icodeailab.com"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )

    return JsonResponse({
        "success": True,
        "message": "Enrollment submitted successfully!"
    })

@csrf_exempt
# def enrollment_store(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "message": "Invalid request"})
 
#     full_name   = request.POST.get("full_name", "").strip()
#     phone       = request.POST.get("phone", "").strip()
#     email       = request.POST.get("email", "").strip()
#     comments    = request.POST.get("comments", "").strip()
#     program_ids = request.POST.getlist("programs")
#     age_bracket_id              = request.POST.get("age_bracket")
#     preferred_registration_date = request.POST.get("preferred_registration_date")  
#     registration_timeline_id    = request.POST.get("registration_timeline")
#     prospective_start_date      = request.POST.get("preferred_start_date")       
#     customized_course           = request.POST.get("customized_course", "no")  
#     status = EnrollmentStatus.objects.filter(code="pending").first()
 
#     age_bracket = None
#     if age_bracket_id:
#         age_bracket = AgeBracket.objects.filter(id=age_bracket_id, is_active=True).first()
    
#     if not age_bracket:
#         age_bracket = AgeBracket.objects.filter(is_active=True).first()
 
#     registration_timeline = None
#     if registration_timeline_id:
#         registration_timeline = RegistrationTimeline.objects.filter(
#             id=registration_timeline_id
#         ).first()
 
#     enrollment = Enrollment.objects.create(
#         full_name=full_name,
#         phone=phone,
#         email=email,
#         comments=comments,
#         status=status,
#         age_bracket=age_bracket,
#         preferred_registration_date=preferred_registration_date or None,
#         registration_timeline=registration_timeline,
#         preferred_start_date=prospective_start_date or None,
#         custom_course_interest=customized_course if customized_course in ("yes", "no") else None,
#     )
 
#     if program_ids:
#         enrollment.programs.set(Program.objects.filter(id__in=program_ids))
 
#     send_mail(
#         subject="Enrollment Received - i-Code",
#         message=(
#             f"Hello {full_name},\n\n"
#             "We have received your enrollment successfully.\n\n"
#             "Our team will review your request and get back to you shortly.\n\n"
#             "Thank you for choosing i-Code."
#         ),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[email],
#         fail_silently=True,
#     )
 
#     return JsonResponse({
#         "success": True,
#         "message": "Enrollment submitted successfully!"
#     })
 
#  TERMS AND CONDITIONS
def terms(request):
    return render(request, 'terms.html')



@require_POST
def newsletter_subscribe(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()

        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required.'}, status=400)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)

        if not created:
            # Already subscribed — don't send email again
            return JsonResponse({'success': False, 'message': 'You are already subscribed!'}, status=200)

        # ✅ Send welcome email only to NEW subscribers
        send_welcome_email(request, email)

        return JsonResponse({'success': True, 'message': 'Subscribed successfully! Check your inbox.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def send_welcome_email(request, email):
    unsubscribe_url = request.build_absolute_uri(f'/newsletter/unsubscribe/{email}/')

    html_content = render_to_string('emails/welcome_newsletter.html', {
        'email': email,
        'unsubscribe_url': unsubscribe_url,
    })

    msg = EmailMultiAlternatives(
        subject='You\'re subscribed! Welcome aboard.',
        body='Thank you for subscribing to our newsletter. You will be receiving updates soon!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# UNSUBSCRIBE
def newsletter_unsubscribe(request, email):
    try:
        subscriber = NewsletterSubscriber.objects.get(email=email)
        
        if not subscriber.is_active:
            # Already unsubscribed
            return render(request, 'emails/unsubscribe.html', {
                'message': 'already',
                'email': email
            })

        subscriber.is_active = False
        subscriber.save()

        return render(request, 'emails/unsubscribe.html', {
            'message': 'success',
            'email': email
        })

    except NewsletterSubscriber.DoesNotExist:
        return render(request, 'emails/unsubscribe.html', {
            'message': 'notfound',
            'email': email
        })
 
# EXTRA SETTINGS
# views.py



# ─── PROGRAM TYPES ───────────────────────────────────────────────────────────

def program_types(request):
    types = ProgramType.objects.all()
    context = {"program_types": types}
    return render(request, "icode-admin/program_types.html", context)


@require_POST
def program_type_store(request):
    try:
        data  = json.loads(request.body)
        name  = data.get("name", "").strip()
        order = data.get("order", 0)

        if not name:
            return JsonResponse({"success": False, "error": "Name is required"})

        if ProgramType.objects.filter(name__iexact=name).exists():
            return JsonResponse({"success": False, "error": "Program type already exists"})

        pt = ProgramType.objects.create(name=name, order=order)

        return JsonResponse({
            "success": True,
            "message": "Program type added",
            "program_type": {"id": pt.id, "name": pt.name, "order": pt.order}
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def program_type_update(request, pk):
    try:
        data  = json.loads(request.body)
        name  = data.get("name", "").strip()
        order = data.get("order", 0)

        if not name:
            return JsonResponse({"success": False, "error": "Name is required"})

        pt = ProgramType.objects.get(pk=pk)

        if ProgramType.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            return JsonResponse({"success": False, "error": "Another type with this name exists"})

        pt.name  = name
        pt.order = order
        pt.save()

        return JsonResponse({
            "success": True,
            "message": "Program type updated",
            "program_type": {"id": pt.id, "name": pt.name, "order": pt.order}
        })

    except ProgramType.DoesNotExist:
        return JsonResponse({"success": False, "error": "Program type not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ─── TERM FEES ────────────────────────────────────────────────────────────────

def term_fees(request):
    fees  = TermFee.objects.select_related("program_type").all()
    types = ProgramType.objects.all()          # for the dropdown in the modal
    context = {"term_fees": fees, "program_types": types}
    return render(request, "icode-admin/term_fees.html", context)


@require_POST
def term_fee_store(request):
    try:
        data            = json.loads(request.body)
        program_type_id = data.get("program_type_id")
        fee_min         = data.get("fee_min")
        fee_max         = data.get("fee_max")

        if not all([program_type_id, fee_min, fee_max]):
            return JsonResponse({"success": False, "error": "All fields are required"})

        if int(fee_max) < int(fee_min):
            return JsonResponse({"success": False, "error": "Max fee cannot be less than min fee"})

        pt = ProgramType.objects.get(pk=program_type_id)

        if TermFee.objects.filter(program_type=pt).exists():
            return JsonResponse({"success": False, "error": "Fee for this program type already exists"})

        fee = TermFee.objects.create(
            program_type=pt,
            fee_min=fee_min,
            fee_max=fee_max
        )

        return JsonResponse({
            "success": True,
            "message": "Fee added",
            "fee": {
                "id":           fee.id,
                "program_type": pt.name,
                "fee_min":      fee.fee_min,
                "fee_max":      fee.fee_max,
                "display_fee":  fee.display_fee
            }
        })

    except ProgramType.DoesNotExist:
        return JsonResponse({"success": False, "error": "Program type not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def term_fee_update(request, pk):
    try:
        data    = json.loads(request.body)
        fee_min = data.get("fee_min")
        fee_max = data.get("fee_max")

        if not all([fee_min, fee_max]):
            return JsonResponse({"success": False, "error": "Both fee fields are required"})

        if int(fee_max) < int(fee_min):
            return JsonResponse({"success": False, "error": "Max fee cannot be less than min fee"})

        fee         = TermFee.objects.get(pk=pk)
        fee.fee_min = fee_min
        fee.fee_max = fee_max
        fee.save()

        return JsonResponse({
            "success": True,
            "message": "Fee updated",
            "fee": {
                "id":          fee.id,
                "fee_min":     fee.fee_min,
                "fee_max":     fee.fee_max,
                "display_fee": fee.display_fee
            }
        })

    except TermFee.DoesNotExist:
        return JsonResponse({"success": False, "error": "Fee not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ─── ADDITIONAL COSTS ─────────────────────────────────────────────────────────

def additional_costs(request):
    costs = AdditionalCost.objects.all()
    context = {"costs": costs}
    return render(request, "icode-admin/additional_costs.html", context)


@require_POST
def additional_cost_store(request):
    try:
        data   = json.loads(request.body)
        name   = data.get("name", "").strip()
        amount = data.get("amount")
        note   = data.get("note", "").strip()
        order  = data.get("order", 0)

        if not name:
            return JsonResponse({"success": False, "error": "Name is required"})
        if not amount:
            return JsonResponse({"success": False, "error": "Amount is required"})

        cost = AdditionalCost.objects.create(
            name=name, amount=amount, note=note, order=order
        )

        return JsonResponse({
            "success": True,
            "message": "Cost added",
            "cost": {
                "id":             cost.id,
                "name":           cost.name,
                "amount":         cost.amount,
                "display_amount": cost.display_amount,
                "note":           cost.note or ""
            }
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def additional_cost_update(request, pk):
    try:
        data   = json.loads(request.body)
        name   = data.get("name", "").strip()
        amount = data.get("amount")
        note   = data.get("note", "").strip()
        order  = data.get("order", 0)

        if not name:
            return JsonResponse({"success": False, "error": "Name is required"})
        if not amount:
            return JsonResponse({"success": False, "error": "Amount is required"})

        cost        = AdditionalCost.objects.get(pk=pk)
        cost.name   = name
        cost.amount = amount
        cost.note   = note
        cost.order  = order
        cost.save()

        return JsonResponse({
            "success": True,
            "message": "Cost updated",
            "cost": {
                "id":             cost.id,
                "name":           cost.name,
                "amount":         cost.amount,
                "display_amount": cost.display_amount,
                "note":           cost.note or ""
            }
        })

    except AdditionalCost.DoesNotExist:
        return JsonResponse({"success": False, "error": "Cost not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ─── FEE CONFIG (singleton) ───────────────────────────────────────────────────

def fee_config(request):
    config = FeeConfig.objects.first()
    context = {"config": config}
    return render(request, "icode-admin/fee_config.html", context)


@require_POST
def fee_config_update(request):
    try:
        data              = json.loads(request.body)
        fees_per_term_min = data.get("fees_per_term_min")
        fees_per_term_max = data.get("fees_per_term_max")
        tagline           = data.get("tagline", "").strip()

        if not all([fees_per_term_min, fees_per_term_max, tagline]):
            return JsonResponse({"success": False, "error": "All fields are required"})

        if int(fees_per_term_max) < int(fees_per_term_min):
            return JsonResponse({"success": False, "error": "Max cannot be less than min"})

        # get_or_create handles first-time setup
        config, _ = FeeConfig.objects.get_or_create(pk=1)
        config.fees_per_term_min = fees_per_term_min
        config.fees_per_term_max = fees_per_term_max
        config.tagline           = tagline
        config.save()

        return JsonResponse({
            "success": True,
            "message": "Fee configuration updated",
            "config": {
                "tagline":       config.tagline,
                "display_range": config.display_range
            }
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
    
def fees_manager(request):
    return render(request, "icode-admin/fees_manager.html", {
        "program_types": ProgramType.objects.all(),
        "term_fees":     TermFee.objects.select_related("program_type").all(),
        "costs":         AdditionalCost.objects.all(),
        "config":        FeeConfig.objects.first(),
    })
    
    

# ─────────────────────────────────────────────────────────────────────────────
# LEVEL
# ─────────────────────────────────────────────────────────────────────────────

def level_list(request):
    levels = Level.objects.all().order_by("order")
    context = {"levels": levels}
    return render(request, "icode-admin/level_list.html", context)


@require_POST
def level_store(request):
    try:
        data  = json.loads(request.body)
        name  = data.get("name", "").strip()
        slug  = data.get("slug", "").strip()
        order = data.get("order", 0)

        if not name:
            return JsonResponse({"success": False, "error": "Name is required"})

        if not slug:
            return JsonResponse({"success": False, "error": "Slug is required"})

        if Level.objects.filter(slug=slug).exists():
            return JsonResponse({"success": False, "error": "Slug already exists"})

        if Level.objects.filter(name=name).exists():
            return JsonResponse({"success": False, "error": "Name already exists"})

        level = Level.objects.create(name=name, slug=slug, order=order)

        return JsonResponse({
            "success": True,
            "message": "Level added successfully",
            "level": {
                "id":    level.id,
                "name":  level.name,
                "slug":  level.slug,
                "order": level.order,
            }
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def level_update(request, pk):
    try:
        level = get_object_or_404(Level, pk=pk)
        data  = json.loads(request.body)
        name  = data.get("name", "").strip()
        slug  = data.get("slug", "").strip()
        order = data.get("order", 0)
        is_active = data.get("is_active", True)

        if not name:
            return JsonResponse({"success": False, "error": "Name is required"})

        if not slug:
            return JsonResponse({"success": False, "error": "Slug is required"})

        if Level.objects.exclude(id=level.id).filter(slug=slug).exists():
            return JsonResponse({"success": False, "error": "Slug already exists"})

        if Level.objects.exclude(id=level.id).filter(name=name).exists():
            return JsonResponse({"success": False, "error": "Name already exists"})

        level.name     = name
        level.slug     = slug
        level.order    = order
        level.save()

        return JsonResponse({"success": True, "message": "Level updated successfully"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ─────────────────────────────────────────────────────────────────────────────
# TOOL TYPE
# ─────────────────────────────────────────────────────────────────────────────

def tool_type_list(request):
    tool_types = ToolType.objects.all().order_by("order")
    context = {"tool_types": tool_types}
    return render(request, "icode-admin/tool_type_list.html", context)


@require_POST
def tool_type_store(request):
    try:
        data  = json.loads(request.body)
        name  = data.get("name", "").strip()
        slug  = data.get("slug", "").strip()
        order = data.get("order", 0)

        if not name:
            return JsonResponse({"success": False, "error": "Name is required"})

        if not slug:
            return JsonResponse({"success": False, "error": "Slug is required"})

        if ToolType.objects.filter(slug=slug).exists():
            return JsonResponse({"success": False, "error": "Slug already exists"})

        if ToolType.objects.filter(name=name).exists():
            return JsonResponse({"success": False, "error": "Name already exists"})

        tool_type = ToolType.objects.create(name=name, slug=slug, order=order)

        return JsonResponse({
            "success": True,
            "message": "Tool type added successfully",
            "tool_type": {
                "id":    tool_type.id,
                "name":  tool_type.name,
                "slug":  tool_type.slug,
                "order": tool_type.order,
            }
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def tool_type_update(request, pk):
    try:
        tool_type = get_object_or_404(ToolType, pk=pk)
        data  = json.loads(request.body)
        name  = data.get("name", "").strip()
        slug  = data.get("slug", "").strip()
        order = data.get("order", 0)

        if not name:
            return JsonResponse({"success": False, "error": "Name is required"})

        if not slug:
            return JsonResponse({"success": False, "error": "Slug is required"})

        if ToolType.objects.exclude(id=tool_type.id).filter(slug=slug).exists():
            return JsonResponse({"success": False, "error": "Slug already exists"})

        if ToolType.objects.exclude(id=tool_type.id).filter(name=name).exists():
            return JsonResponse({"success": False, "error": "Name already exists"})

        tool_type.name  = name
        tool_type.slug  = slug
        tool_type.order = order
        tool_type.save()

        return JsonResponse({"success": True, "message": "Tool type updated successfully"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAM TOOL
# ─────────────────────────────────────────────────────────────────────────────

def program_tool_list(request):
    program_tools = (
        ProgramTool.objects
        .select_related("program", "tool_type")
        .order_by("program__order", "order")
    )
    programs   = Program.objects.filter(is_active=True).order_by("order")
    tool_types = ToolType.objects.all().order_by("order")

    context = {
        "program_tools": program_tools,
        "programs":      programs,
        "tool_types":    tool_types,
    }
    return render(request, "icode-admin/program_tool_list.html", context)


@require_POST
def program_tool_store(request):
    try:
        data          = json.loads(request.body)
        name          = data.get("name", "").strip()
        program_id    = data.get("program_id")
        tool_type_id  = data.get("tool_type_id")
        order         = data.get("order", 0)

        if not name:
            return JsonResponse({"success": False, "error": "Tool name is required"})

        if not program_id:
            return JsonResponse({"success": False, "error": "Programme is required"})

        program   = get_object_or_404(Program,  pk=program_id)
        tool_type = get_object_or_404(ToolType, pk=tool_type_id) if tool_type_id else None

        tool = ProgramTool.objects.create(
            name=name,
            program=program,
            tool_type=tool_type,
            order=order,
        )

        return JsonResponse({
            "success": True,
            "message": "Tool added successfully",
            "tool": {
                "id":             tool.id,
                "name":           tool.name,
                "program_id":     program.id,
                "program_name":   program.name,
                "tool_type_id":   tool_type.id   if tool_type else None,
                "tool_type_name": tool_type.name if tool_type else "—",
                "order":          tool.order,
            }
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def program_tool_update(request, pk):
    try:
        tool         = get_object_or_404(ProgramTool, pk=pk)
        data         = json.loads(request.body)
        name         = data.get("name", "").strip()
        program_id   = data.get("program_id")
        tool_type_id = data.get("tool_type_id")
        order        = data.get("order", 0)

        if not name:
            return JsonResponse({"success": False, "error": "Tool name is required"})

        if not program_id:
            return JsonResponse({"success": False, "error": "Programme is required"})

        tool.name      = name
        tool.program   = get_object_or_404(Program, pk=program_id)
        tool.tool_type = get_object_or_404(ToolType, pk=tool_type_id) if tool_type_id else None
        tool.order     = order
        tool.save()

        return JsonResponse({"success": True, "message": "Tool updated successfully"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
        
        
# TESTIMONIALS SUBMISSION
@require_POST
def submit_testimonial(request):
    name    = request.POST.get("author_name", "").strip()
    role    = request.POST.get("author_role", "").strip()
    content = request.POST.get("content", "").strip()
    rating  = request.POST.get("rating", "5")

    if name and role and content:
        try:
            rating = int(rating)
            rating = max(1, min(5, rating))
        except ValueError:
            rating = 5

        # is_active=False so you can moderate before publishing
        Testimonial.objects.create(
            author_name=name,
            author_role=role,
            content=content,
            rating=rating,
            is_active=False,   # pending moderation
        )
        messages.success(request, "Thank you! Your testimonial is pending review.")
    else:
        messages.error(request, "Please fill in all required fields.")

    return redirect(request.META.get("HTTP_REFERER", "/"))
    
    



# ── List page ─────────────────────────────────────────────────────────────────
@staff_member_required
def testimonials_admin(request):
    testimonials  = Testimonial.objects.all().order_by("order", "id")
    total_count   = testimonials.count()
    active_count  = testimonials.filter(is_active=True).count()
    pending_count = total_count - active_count

    return render(request, "icode-admin/testimonials_admin.html", {
        "testimonials":  testimonials,
        "total_count":   total_count,
        "active_count":  active_count,
        "pending_count": pending_count,
    })


# ── Toggle is_active ───────────────────────────────────────────────────────────
@staff_member_required
@require_POST
def testimonial_toggle(request, pk):
    try:
        t = Testimonial.objects.get(pk=pk)
        data = json.loads(request.body)
        raw = data.get("is_active")
        # Handle both JSON bool (true/false) and accidental strings
        if isinstance(raw, bool):
            t.is_active = raw
        else:
            t.is_active = str(raw).lower() in ("true", "1", "yes")
        t.save(update_fields=["is_active"])
        return JsonResponse({"success": True, "is_active": t.is_active})
    except Testimonial.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"success": False, "error": "Invalid payload"}, status=400)


# ── Delete ─────────────────────────────────────────────────────────────────────
@staff_member_required
@require_POST
def testimonial_delete(request, pk):
    try:
        Testimonial.objects.get(pk=pk).delete()
        return JsonResponse({"success": True})
    except Testimonial.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)
        


def bootcamp_2026(request):
    
    brackets = AgeBracket.objects.all().order_by("order")
    programs = Program.objects.all()
    timelines = RegistrationTimeline.objects.all()
    testimonials = Testimonial.objects.filter(is_active=True)
    return render(request, 'icode-admin/bootcamp_2026.html', {'brackets': brackets, 'programs':programs, 'timelines':timelines,"testimonials": testimonials})
    
    
# ── GALLERY VIEWS ──
@login_required
def gallery_admin(request):
    items = GalleryItem.objects.all()
    this_month  = timezone.now().date().replace(day=1)
    total_items  = items.count()
    total_images = items.filter(type='image').count()
    total_videos = items.filter(type='video').count()
    recent_count = items.filter(uploaded_at__date__gte=this_month).count()

    return render(request, 'icode-admin/gallery_admin.html', {
        'items':         items,
        'total_items':   total_items,
        'total_images':  total_images,
        'total_videos':  total_videos,
        'recent_count':  recent_count,
    })


@login_required
def gallery_upload(request):
    if request.method == 'POST':
        title     = request.POST.get('title', '').strip()
        date      = request.POST.get('date')
        type_     = request.POST.get('type', 'image')
        category  = request.POST.get('category', 'event')
        caption   = request.POST.get('caption', '').strip()
        media     = request.FILES.get('media')
        thumbnail = request.FILES.get('thumbnail')

        if not title or not date or not media:
            messages.error(request, 'Title, date, and media file are required.')
            return redirect('gallery_admin')

        GalleryItem.objects.create(
            title     = title,
            date      = date,
            type      = type_,
            category  = category,
            caption   = caption,
            media     = media,
            thumbnail = thumbnail if thumbnail else None,
        )
        messages.success(request, f'"{title}" uploaded successfully.')
    return redirect('gallery_admin')


@login_required
def gallery_delete(request, pk):
    if request.method == 'POST':
        item = get_object_or_404(GalleryItem, pk=pk)
        title = item.title
        if item.media:
            item.media.delete(save=False)
        if item.thumbnail:
            item.thumbnail.delete(save=False)
        item.delete()
        messages.success(request, f'"{title}" deleted.')
    return redirect('gallery_admin')
    
def team_icode(request):
    members = TeamMember.objects.filter(is_active=True) | TeamMember.objects.filter(is_active=False)
    members = TeamMember.objects.all()         

    # dept breakdown for stats bar
    dept_counts = {
        row['dept']: row['count']
        for row in TeamMember.objects.values('dept').annotate(count=Count('id'))
    }

    context = {
        'members':       members,
        'total':         members.count(),
        'active_count':  members.filter(is_active=True).count(),
        'featured_count': members.filter(is_featured=True).count(),
        'dept_counts':   dept_counts,
    }
    return render(request, 'icode-admin/teams.html', context)


# ─────────────────────────────────────────────
# Detail  (returns JSON for edit modal)
# ─────────────────────────────────────────────
@login_required
@staff_member_required
@require_GET
def team_member_detail(request, pk):
    member = get_object_or_404(TeamMember, pk=pk)
    return JsonResponse({
        'id':          member.id,
        'name':        member.name,
        'title':       member.title,
        'role':        member.role,
        'dept':        member.dept,
        'initials':    member.initials,
        'stripe':      member.stripe,
        'bio':         member.bio,
        'credentials': member.credentials,
        'specialisms': member.specialisms,
        'is_active':   member.is_active,
        'is_featured': member.is_featured,
        'order':       member.order,
        'photo_url':   member.photo.url if member.photo else None,
    })


# ─────────────────────────────────────────────
# Add  (POST, returns JSON)

@staff_member_required
@require_POST
def team_member_add(request):
    try:
        data = request.POST
        member = TeamMember(
            name        = data.get('name', '').strip(),
            title       = data.get('title', '').strip(),
            role        = data.get('role', 'instructor'),
            dept        = data.get('dept', 'tech'),
            initials    = data.get('initials', '').strip(),
            stripe      = data.get('stripe', 'teal'),
            bio         = data.get('bio', '').strip(),
            credentials = data.get('credentials', '').strip(),
            specialisms = data.get('specialisms', '').strip(),
            is_active   = data.get('is_active') in ('1', 'true', 'True', True),
            is_featured = data.get('is_featured') in ('1', 'true', 'True', True),
            order       = int(data.get('order') or 0),
        )
        if 'photo' in request.FILES:
            member.photo = request.FILES['photo']

        # basic validation
        errors = _validate(member)
        if errors:
            return JsonResponse({'success': False, 'error': '; '.join(errors)}, status=400)

        member.save()
        return JsonResponse({'success': True, 'message': f'{member.name} added successfully.', 'id': member.id})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ─────────────────────────────────────────────
# Update  (POST, returns JSON)
# ─────────────────────────────────────────────
@staff_member_required
@require_POST
def team_member_update(request, pk):
    member = get_object_or_404(TeamMember, pk=pk)
    try:
        data = request.POST
        member.name        = data.get('name', '').strip()
        member.title       = data.get('title', '').strip()
        member.role        = data.get('role', member.role)
        member.dept        = data.get('dept', member.dept)
        member.stripe      = data.get('stripe', member.stripe)
        member.bio         = data.get('bio', '').strip()
        member.credentials = data.get('credentials', '').strip()
        member.specialisms = data.get('specialisms', '').strip()
        member.is_active   = data.get('is_active') in ('1', 'true', 'True', True)
        member.is_featured = data.get('is_featured') in ('1', 'true', 'True', True)
        member.order       = int(data.get('order') or 0)

        raw_initials = data.get('initials', '').strip()
        if raw_initials:
            member.initials = raw_initials
        else:
            member.initials = ''   

        if 'photo' in request.FILES:
          
            if member.photo:
                member.photo.delete(save=False)
            member.photo = request.FILES['photo']

        errors = _validate(member)
        if errors:
            return JsonResponse({'success': False, 'error': '; '.join(errors)}, status=400)

        member.save()
        return JsonResponse({'success': True, 'message': f'{member.name} updated successfully.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ─────────────────────────────────────────────
# Toggle a boolean field  (is_active / is_featured)
# ─────────────────────────────────────────────
@login_required
@staff_member_required
@require_POST
def team_member_toggle(request, pk):
    member = get_object_or_404(TeamMember, pk=pk)
    try:
        body  = json.loads(request.body)
        field = body.get('field')
        value = body.get('value')

        if field not in ('is_active', 'is_featured'):
            return JsonResponse({'success': False, 'error': 'Invalid field.'}, status=400)

        setattr(member, field, bool(value))
        member.save(update_fields=[field])

        label = 'active' if field == 'is_active' else 'featured'
        state = 'enabled' if value else 'disabled'
        return JsonResponse({'success': True, 'message': f'{member.name} {label} {state}.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ─────────────────────────────────────────────
# Delete  (POST, returns JSON)
# ─────────────────────────────────────────────
@login_required
@staff_member_required
@require_POST
def team_member_delete(request, pk):
    member = get_object_or_404(TeamMember, pk=pk)
    try:
        name = member.name
        if member.photo:
            member.photo.delete(save=False)   # clean up uploaded file
        member.delete()
        return JsonResponse({'success': True, 'message': f'{name} deleted.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ─────────────────────────────────────────────
# Internal validation helper
# ─────────────────────────────────────────────
def _validate(member):
    errors = []
    if not member.name:
        errors.append('Name is required.')
    if not member.title:
        errors.append('Title is required.')
    if not member.bio:
        errors.append('Bio is required.')
    if member.role not in dict(TeamMember.ROLE_CHOICES):
        errors.append('Invalid role.')
    if member.stripe not in dict(TeamMember.STRIPE_CHOICES):
        errors.append('Invalid stripe colour.')
    return errors
    

    