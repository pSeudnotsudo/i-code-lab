from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from .models import *
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def index(request):
    """
    Passes everything the homepage template needs:
    - featured courses for the Popular Classes grid
    - approved + featured testimonials
    - editable stats
    - next upcoming scheduled class for the hero floating card
    - site settings for hero copy and footer
    - newsletter form for footer
    """
    settings      = SiteSettings.get()
    courses       = Course.objects.filter(is_active=True, is_featured=True).order_by("order")
    testimonials  = Testimonial.objects.filter(is_featured=True, is_approved=True)
    stats         = Stat.objects.all()
    # newsletter_form = NewsletterForm()

    upcoming_class = (
        ScheduledClass.objects
        .filter(is_active=True, scheduled_time__gte=timezone.now())
        .select_related("course")
        .first()
    )
    classes = (
    ScheduledClass.objects
    .filter(is_active=True, scheduled_time__gte=timezone.now())
    .select_related("course")
    .order_by("scheduled_time")  # all upcoming, soonest first
    )
    students = Enrollment.objects.count
    courses_count = Course.objects.count


    # Handle newsletter POST (footer form is on every page via the footer partial)
    # if request.method == "POST" and "newsletter_submit" in request.POST:
    #     newsletter_form = NewsletterForm(request.POST)
    #     if newsletter_form.is_valid():
    #         newsletter_form.save()
    #         messages.success(request, "You're subscribed! Thanks for joining.")
    #         return redirect("index")
        # Fall through — form with errors re-rendered below

    return render(request, "index.html", {
        "settings":        settings,
        "courses":         courses,
        "courses_count":   courses_count,
        "students":  students,
        "testimonials":    testimonials,
        "stats":           stats,
        "upcoming_class":  upcoming_class,
        "classes":  classes,
        # "newsletter_form": newsletter_form,
    })




def programs(request):
    """
    Programs listing page.
    All dummy data is hardcoded in programs.html.
    When your models are ready, pass real querysets here.

   
    """
    return render(request, 'programs.html', {})

def course_detail(request, slug):  
    course = get_object_or_404(Course, slug=slug)  
    return render(request, 'course_detail.html', {'course': course})


def newsletter_subscribe(request):
    
    return render(request, 'course_detail', {})


def programs(request):
    courses = Course.objects.all().order_by('-id')
    students = Enrollment.objects.count

    program_types = Course.objects.values_list('program_type', flat=True).distinct()
    
    program_type = request.GET.get('type')
    if program_type and program_type != 'all':
        courses = courses.filter(type=program_type)

    context = {
        'courses': courses,
        'program_types': program_types,
        'students':students
    }
    return render(request, 'courses.html', context)




@require_POST
def enroll_ajax(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'errors': {'__all__': ['Invalid request.']}}, status=400)

    # Manual validation
    errors = {}

    full_name = body.get('full_name', '').strip()
    email     = body.get('email', '').strip()
    phone     = body.get('phone', '').strip()
    child_name = body.get('child_name', '').strip()
    child_age  = body.get('child_age')
    message   = body.get('message', '').strip()

    if not full_name:
        errors['full_name'] = ['Full name is required.']

    if not email:
        errors['email'] = ['Email is required.']
    elif '@' not in email:
        errors['email'] = ['Enter a valid email address.']

    if child_age is not None:
        try:
            child_age = int(child_age)
            if child_age < 1:
                errors['child_age'] = ['Age must be a positive number.']
        except (ValueError, TypeError):
            errors['child_age'] = ['Enter a valid age.']
    else:
        child_age = None

    if errors:
        return JsonResponse({'errors': errors}, status=400)
    
    # After validation passes, before saving — add this check:
    if Enrollment.objects.filter(course=course, email=email).exists():
        return JsonResponse({'error': 'This email is already enrolled in this class.'}, status=409)



    Enrollment.objects.create(
        course     = course,
        full_name  = full_name,
        email      = email,
        phone      = phone,
        child_name = child_name,
        child_age  = child_age,
        message    = message,
    )

    return JsonResponse({'status': 'ok'}, status=201)