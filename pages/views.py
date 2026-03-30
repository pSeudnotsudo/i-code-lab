from django.shortcuts import render


def index(request):
    """
    Landing page view.
    All dummy data is hardcoded in landing.html.
    When your models are ready, pass real querysets here and
    activate the commented-out {% for %} loops in the template.

    Example (when models exist):
    ─────────────────────────────
    from .models import Program, Testimonial, SiteSettings

    context = {
        'programs':     Program.objects.filter(is_active=True).order_by('order'),
        'testimonials': Testimonial.objects.filter(is_published=True)[:3],
        'stats':        SiteSettings.objects.first().stats_as_list(),
    }
    return render(request, 'landing.html', context)
    ─────────────────────────────
    """
    return render(request, 'index.html', {})


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
