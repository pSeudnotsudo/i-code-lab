"""
admin_views.py
~~~~~~~~~~~~~~
All AJAX views consumed by the I-code admin dashboard.

Every view:
  • Requires POST (for mutations) or GET (for list/read).
  • Returns JsonResponse — no page renders except `dashboard`.
  • Is guarded by `staff_required` so only staff/superusers can call them.

Wire these in urls.py under the admin-ajax/ prefix.
"""

import json
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from .models import *

# ─────────────────────────────────────────────
#  GUARD  — staff only
# ─────────────────────────────────────────────

def staff_required(view_func):
    """
    Decorator: redirects unauthenticated users to the login page.
    Returns 403 JSON for authenticated non-staff callers.
    AJAX requests always get JSON regardless of auth state.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if not request.user.is_authenticated:
            if is_ajax:
                return JsonResponse({"error": "Login required"}, status=401)
            from django.shortcuts import redirect
            from django.urls import reverse
            login_url = reverse("icode:admin_login")
            return redirect(f"{login_url}?next={request.path}")

        if not request.user.is_staff:
            return JsonResponse({"error": "Staff access required"}, status=403)

        return view_func(request, *args, **kwargs)
    return wrapper


def ajax_required(view_func):
    """Decorator: 400 if not an XMLHttpRequest (optional extra guard)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "AJAX only"}, status=400)
        return view_func(request, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────
#  DASHBOARD  (HTML page — not AJAX)
# ─────────────────────────────────────────────

@staff_required
def dashboard(request):
    """Render the admin dashboard SPA shell."""
    return render(request, "admin/icode/dashboard.html")


# ─────────────────────────────────────────────
#  DASHBOARD STATS SUMMARY
# ─────────────────────────────────────────────

@staff_required
@require_GET
def stats_summary(request):
    """
    GET /admin-ajax/stats-summary/
    Returns counts used by the dashboard overview cards.
    """
    return JsonResponse({
        "active_courses":    Course.objects.filter(is_active=True).count(),
        "total_enrollments": Enrollment.objects.count(),
        "pending_reviews":   Review.objects.filter(is_approved=False).count(),
        "subscribers":       NewsletterSubscriber.objects.filter(is_active=True).count(),
        "upcoming_classes":  ScheduledClass.objects.filter(is_active=True).count(),
    })


# ─────────────────────────────────────────────
#  COURSES
# ─────────────────────────────────────────────

@staff_required
@require_GET
def course_list(request):
    """
    GET /admin-ajax/courses/
    Returns all courses ordered by display order then title.
    """
    courses = Course.objects.all().values(
        "id", "title", "slug", "program_type", "level",
        "age_min", "age_max", "price", "duration",
        "instructor_name", "is_active", "is_featured", "order",
    )
    return JsonResponse({"courses": list(courses)})


@staff_required
@require_POST
def course_add(request):
    """
    POST /admin-ajax/courses/add/
    Creates a new Course from form data.
    """
    p = request.POST
    try:
        course = Course.objects.create(
            title=p["title"],
            slug=p["slug"],
            description=p.get("description", ""),
            price=p.get("price", 0),
            duration=p.get("duration", ""),
            program_type=p["program_type"],
            level=p.get("level", "all"),
            age_min=int(p.get("age_min", 7)),
            age_max=int(p.get("age_max", 18)),
            instructor_name=p["instructor_name"],
            is_active=p.get("is_active", "true") == "true",
            is_featured=p.get("is_featured", "false") == "true",
            order=int(p.get("order", 0)),
        )
        return JsonResponse({"status": "ok", "id": course.pk, "title": course.title})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@staff_required
@require_POST
def course_delete(request, pk):
    """
    POST /admin-ajax/courses/<pk>/delete/
    Hard-deletes a course (consider soft-delete via is_active=False in production).
    """
    try:
        Course.objects.filter(pk=pk).delete()
        return JsonResponse({"status": "ok"})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)


# ─────────────────────────────────────────────
#  SCHEDULED CLASSES
# ─────────────────────────────────────────────

@staff_required
@require_GET
def scheduled_list(request):
    items = ScheduledClass.objects.select_related("course").values(
        "id", "title", "course__title", "instructor_name",
        "scheduled_time", "is_active",
    )
    return JsonResponse({"scheduled": list(items)})


@staff_required
@require_POST
def scheduled_add(request):
    p = request.POST
    try:
        course = Course.objects.get(pk=p["course"])
        sc = ScheduledClass.objects.create(
            course=course,
            title=p["title"],
            instructor_name=p["instructor_name"],
            scheduled_time=p["scheduled_time"],
            is_active=p.get("is_active", "true") == "true",
        )
        return JsonResponse({"status": "ok", "id": sc.pk})
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course not found"}, status=404)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@staff_required
@require_POST
def scheduled_delete(request, pk):
    ScheduledClass.objects.filter(pk=pk).delete()
    return JsonResponse({"status": "ok"})


# ─────────────────────────────────────────────
#  STATS STRIP
# ─────────────────────────────────────────────

@staff_required
@require_GET
def stat_list(request):
    stats = Stat.objects.all().values("id", "label", "value", "order")
    return JsonResponse({"stats": list(stats)})


@staff_required
@require_POST
def stat_add(request):
    p = request.POST
    try:
        stat = Stat.objects.create(
            label=p["label"],
            value=p["value"],
            order=int(p.get("order", 0)),
        )
        return JsonResponse({"status": "ok", "id": stat.pk})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@staff_required
@require_POST
def stat_delete(request, pk):
    Stat.objects.filter(pk=pk).delete()
    return JsonResponse({"status": "ok"})


# ─────────────────────────────────────────────
#  ENROLLMENTS  (read-only in admin)
# ─────────────────────────────────────────────

@staff_required
@require_GET
def enrollment_list(request):
    enrollments = Enrollment.objects.select_related("course").values(
        "id", "full_name", "email", "phone",
        "child_name", "child_age", "message",
        "course__title", "enrolled_at",
    ).order_by("-enrolled_at")
    return JsonResponse({"enrollments": list(enrollments)})


# ─────────────────────────────────────────────
#  REVIEWS
# ─────────────────────────────────────────────

@staff_required
@require_GET
def review_list(request):
    reviews = Review.objects.select_related("course").values(
        "id", "full_name", "email", "rating",
        "comment", "is_approved", "created_at",
        "course__title",
    ).order_by("-created_at")
    return JsonResponse({"reviews": list(reviews)})


@staff_required
@require_POST
def review_approve(request, pk):
    updated = Review.objects.filter(pk=pk).update(is_approved=True)
    if not updated:
        return JsonResponse({"error": "Review not found"}, status=404)
    return JsonResponse({"status": "ok"})


@staff_required
@require_POST
def review_delete(request, pk):
    Review.objects.filter(pk=pk).delete()
    return JsonResponse({"status": "ok"})


# ─────────────────────────────────────────────
#  TESTIMONIALS
# ─────────────────────────────────────────────

@staff_required
@require_GET
def testimonial_list(request):
    items = Testimonial.objects.select_related("course").values(
        "id", "full_name", "occupation", "rating",
        "comment", "is_featured", "is_approved",
        "order", "created_at", "course__title",
    )
    return JsonResponse({"testimonials": list(items)})


@staff_required
@require_POST
def testimonial_add(request):
    p = request.POST
    try:
        course = None
        if p.get("course"):
            course = Course.objects.get(pk=p["course"])
        t = Testimonial.objects.create(
            course=course,
            full_name=p["full_name"],
            occupation=p.get("occupation", ""),
            rating=int(p.get("rating", 5)),
            comment=p["comment"],
            is_featured=p.get("is_featured", "true") == "true",
            is_approved=p.get("is_approved", "true") == "true",
            order=int(p.get("order", 0)),
        )
        return JsonResponse({"status": "ok", "id": t.pk})
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course not found"}, status=404)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@staff_required
@require_POST
def testimonial_delete(request, pk):
    Testimonial.objects.filter(pk=pk).delete()
    return JsonResponse({"status": "ok"})


# ─────────────────────────────────────────────
#  NEWSLETTER
# ─────────────────────────────────────────────

@staff_required
@require_GET
def newsletter_list(request):
    subs = NewsletterSubscriber.objects.values(
        "id", "email", "subscribed_at", "is_active"
    ).order_by("-subscribed_at")
    return JsonResponse({"subscribers": list(subs)})


@staff_required
@require_POST
def newsletter_delete(request, pk):
    NewsletterSubscriber.objects.filter(pk=pk).delete()
    return JsonResponse({"status": "ok"})


# ─────────────────────────────────────────────
#  SITE SETTINGS
# ─────────────────────────────────────────────

@staff_required
@require_GET
def settings_get(request):
    s = SiteSettings.get()
    return JsonResponse({
        "site_name":           s.site_name,
        "hero_heading_accent": s.hero_heading_accent,
        "hero_heading_main":   s.hero_heading_main,
        "hero_subtext":        s.hero_subtext,
        "footer_description":  s.footer_description,
        "contact_email":       s.contact_email,
        "phone_number":        s.phone_number,
        "address":             s.address,
        "facebook_url":        s.facebook_url,
        "twitter_url":         s.twitter_url,
        "instagram_url":       s.instagram_url,
        "linkedin_url":        s.linkedin_url,
    })


@staff_required
@require_POST
def settings_update(request):
    p = request.POST
    s = SiteSettings.get()
    try:
        s.site_name           = p.get("site_name", s.site_name)
        s.hero_heading_accent = p.get("hero_heading_accent", s.hero_heading_accent)
        s.hero_heading_main   = p.get("hero_heading_main", s.hero_heading_main)
        s.hero_subtext        = p.get("hero_subtext", s.hero_subtext)
        s.footer_description  = p.get("footer_description", s.footer_description)
        s.contact_email       = p.get("contact_email", s.contact_email)
        s.phone_number        = p.get("phone_number", s.phone_number)
        s.address             = p.get("address", s.address)
        s.facebook_url        = p.get("facebook_url", s.facebook_url)
        s.twitter_url         = p.get("twitter_url", s.twitter_url)
        s.instagram_url       = p.get("instagram_url", s.instagram_url)
        s.linkedin_url        = p.get("linkedin_url", s.linkedin_url)
        s.save()
        return JsonResponse({"status": "ok"})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)