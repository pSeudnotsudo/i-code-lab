
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# ─────────────────────────────────────────────
#  CHOICES
# ─────────────────────────────────────────────

PROGRAM_CHOICES = [
    ("coding",        "Coding"),
    ("robotics",      "Robotics"),
    ("cybersecurity", "Cybersecurity"),
    ("drone",         "Drone Training"),
    ("ai",            "Artificial Intelligence"),
    ("flexible",      "Flexible Schedules"),
]

LEVEL_CHOICES = [
    ("all",          "All Levels"),
    ("beginner",     "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced",     "Advanced"),
]

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]


# ─────────────────────────────────────────────
#  SITE SETTINGS  (singleton – admin editable)
# ─────────────────────────────────────────────

class SiteSettings(models.Model):
    """
    One row only. Admin edits hero copy, contact info, opening hours
    without touching code. Enforce singleton via clean().
    """
    site_name            = models.CharField(max_length=100, default="I-code")
    hero_heading_accent  = models.CharField(
        max_length=120, default="Inspiring Kids",
        help_text="The orange-coloured first part of the hero heading"
    )
    hero_heading_main    = models.CharField(
        max_length=200, default="to Build the Future with Technology"
    )
    hero_subtext         = models.TextField(
        default=(
            "I-code is a hands-on in-person tech school for young innovators "
            "aged 7–18. We offer classes in Coding, Robotics, AI, Cybersecurity, "
            "and Drone Training — from beginner to advanced."
        )
    )
    footer_description   = models.TextField(
        default=(
            "Inspiring young innovators aged 7–18 to build the future through "
            "hands-on tech education."
        )
    )
    contact_email        = models.EmailField(default="contact@icode.com")
    phone_number         = models.CharField(max_length=30, default="+1 (555) 123-4567")
    address              = models.CharField(
        max_length=255, default="Open Mon–Fri 8:30am–8:30pm · Weekends 8:30am–4pm"
    )
    facebook_url         = models.URLField(blank=True)
    twitter_url          = models.URLField(blank=True)
    instagram_url        = models.URLField(blank=True)
    linkedin_url         = models.URLField(blank=True)

    class Meta:
        verbose_name        = "Site Settings"
        verbose_name_plural = "Site Settings"

    def clean(self):
        # Enforce singleton
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("Only one SiteSettings instance is allowed.")

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get(cls):
        """Safe helper used in views: SiteSettings.get()"""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ─────────────────────────────────────────────
#  STAT  (editable numbers on the stats strip)
# ─────────────────────────────────────────────

class Stat(models.Model):
    label = models.CharField(max_length=80, help_text='e.g. "Students Enrolled"')
    value = models.CharField(max_length=20, help_text='e.g. "500+" or "98%"')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name        = "Stat"
        verbose_name_plural = "Stats"

    def __str__(self):
        return f"{self.value} — {self.label}"


# ─────────────────────────────────────────────
#  COURSE
# ─────────────────────────────────────────────

class Course(models.Model):
    title        = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True)
    description  = models.TextField()
    # thumbnail    = models.ImageField(upload_to="courses/thumbnails/")
    price        = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duration     = models.CharField(max_length=50, help_text='e.g. "8 weeks"')
    program_type = models.CharField(max_length=20, choices=PROGRAM_CHOICES)
    level        = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="all")
    age_min      = models.PositiveSmallIntegerField(default=7)
    age_max      = models.PositiveSmallIntegerField(default=18)
    instructor_name = models.CharField(
        max_length=120,
        help_text="Instructor full name (no login system)"
    )
    is_active    = models.BooleanField(default=True)
    is_featured  = models.BooleanField(
        default=False,
        help_text="Show on homepage Popular Classes section"
    )
    order        = models.PositiveSmallIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if not reviews.exists():
            return None
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def students_enrolled(self):
        """Count of approved enrollments — used in template as course.students_enrolled"""
        return self.enrollments.count()


# ─────────────────────────────────────────────
#  ENROLLMENT  (visitor signs up for a course)
# ─────────────────────────────────────────────

class Enrollment(models.Model):
    """
    No login required — we store the visitor's name & email.
    Admin can see who enrolled from the Django admin.
    """
    course      = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    full_name   = models.CharField(max_length=120)
    email       = models.EmailField()
    phone       = models.CharField(max_length=30, blank=True)
    child_name  = models.CharField(
        max_length=120, blank=True,
        help_text="Child's name if enrolling on behalf of someone"
    )
    child_age   = models.PositiveSmallIntegerField(null=True, blank=True)
    message     = models.TextField(blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.full_name} → {self.course.title}"


# ─────────────────────────────────────────────
#  REVIEW  (public star-rating form, no login)
# ─────────────────────────────────────────────

class Review(models.Model):
    """
    Visitor submits name + email + rating + comment via a form on the
    course detail page. is_approved=False until admin ticks it.
    The homepage testimonials section uses Testimonial (below) instead —
    admin hand-picks those.
    """
    course      = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="reviews"
    )
    full_name   = models.CharField(max_length=120)
    email       = models.EmailField(help_text="Not shown publicly")
    rating      = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment     = models.TextField()
    is_approved = models.BooleanField(
        default=False,
        help_text="Tick to publish this review publicly"
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.course.title} ({self.rating}★)"


# ─────────────────────────────────────────────
#  TESTIMONIAL  (homepage featured quotes)
# ─────────────────────────────────────────────

class Testimonial(models.Model):
    """
    Admin creates these manually OR promotes a Review into one.
    is_featured controls homepage visibility.
    Avatar is optional — fallback to initials in the template.
    """
    course      = models.ForeignKey(
        Course, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="testimonials"
    )
    full_name   = models.CharField(max_length=120)
    occupation  = models.CharField(
        max_length=120, blank=True,
        help_text='e.g. "Parent of Alex, age 10"'
    )
    # avatar      = models.ImageField(
    #     upload_to="testimonials/avatars/", blank=True, null=True
    # )
    rating      = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment     = models.TextField()
    is_featured = models.BooleanField(
        default=True,
        help_text="Show on homepage"
    )
    is_approved = models.BooleanField(default=True)
    order       = models.PositiveSmallIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.rating}★"


# ─────────────────────────────────────────────
#  SCHEDULED CLASS  (floating card on hero)
# ─────────────────────────────────────────────

class ScheduledClass(models.Model):
    """
    Admin adds upcoming classes. The view passes the next upcoming
    one as `upcoming_class` context — powers the floating hero card.
    """
    course          = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="scheduled_classes"
    )
    title           = models.CharField(
        max_length=200,
        help_text='Override title, e.g. "Robotics Workshop — Beginners"'
    )
    instructor_name = models.CharField(max_length=120)
    # instructor_avatar = models.ImageField(
    #     upload_to="instructors/", blank=True, null=True
    # )
    scheduled_time  = models.DateTimeField()
    is_active       = models.BooleanField(default=True)

    class Meta:
        ordering = ["scheduled_time"]

    def __str__(self):
        return f"{self.title} @ {self.scheduled_time:%d %b %Y %H:%M}"


# ─────────────────────────────────────────────
#  NEWSLETTER SUBSCRIBER
# ─────────────────────────────────────────────

class NewsletterSubscriber(models.Model):
    email         = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active     = models.BooleanField(default=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email