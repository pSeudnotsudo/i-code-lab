from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from .models import *


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

    Example (when models exist):
    ─────────────────────────────
    from .models import Program, Schedule, FAQ

    context = {
        'programs':  Program.objects.filter(is_active=True).order_by('order'),
        'schedule':  Schedule.objects.filter(is_active=True).order_by('day_order', 'time'),
        'faqs':      FAQ.objects.filter(page='programs').order_by('order'),
    }
    return render(request, 'programs.html', context)
    ─────────────────────────────
    """
    return render(request, 'programs.html', {})

def course_detail(request):
    
    return render(request, 'course_detail', {})


def newsletter_subscribe(request):
    
    return render(request, 'course_detail', {})
