from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    STUDENT = 'student'
    PARENT  = 'parent'
    ADMIN   = 'admin'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (PARENT,  'Parent'),
        (ADMIN,   'Admin'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    is_email_verified = models.BooleanField(default=False)
    
    first_name = models.CharField(max_length=150, blank=False)
    last_name  = models.CharField(max_length=150, blank=False)
    
    # Phone details
    phone      = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"


# ─────────────────────────────────────────────
# COURSES & CLASSES
# ─────────────────────────────────────────────

class Course(models.Model):
    """A top-level subject or programme (e.g. "Mathematics Grade 5")."""

    LEVEL_CHOICES = [
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
    ]

    title        = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True)
    description  = models.TextField(blank=True)
    level        = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True)
    thumbnail    = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Curriculum(models.Model):
    """Downloadable curriculum document attached to a course."""

    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='curricula')
    title       = models.CharField(max_length=200)
    file        = models.FileField(upload_to='curricula/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} – {self.title}"


class SchoolClass(models.Model):
    """
    A specific class instance under a course.
    TYPE can be a regular class, masterclass, workshop, etc.
    """

    CLASS_TYPE_CHOICES = [
        ('regular',     'Regular Class'),
        ('masterclass', 'Master Class'),
        ('workshop',    'Workshop'),
        ('bootcamp',    'Boot Camp'),
    ]

    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    title       = models.CharField(max_length=200)
    class_type  = models.CharField(max_length=20, choices=CLASS_TYPE_CHOICES, default='regular')
    description = models.TextField(blank=True)
    instructor  = models.CharField(max_length=200, blank=True)
    capacity    = models.PositiveIntegerField(default=30)
    start_date  = models.DateField(null=True, blank=True)
    end_date    = models.DateField(null=True, blank=True)
    schedule    = models.CharField(max_length=255, blank=True, help_text="e.g. Mon/Wed 4pm–5pm")
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_class_type_display()}] {self.title}"

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status='approved').count()

    @property
    def is_full(self):
        return self.enrolled_count >= self.capacity


# ─────────────────────────────────────────────
# ENROLLMENT  (Students)
# ─────────────────────────────────────────────

class Enrollment(models.Model):
    """A student enrolls in a SchoolClass."""

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('approved',  'Approved'),
        ('rejected',  'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    student      = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': CustomUser.STUDENT},
    )
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='enrollments')
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    enrolled_at  = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    notes        = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'school_class')

    def __str__(self):
        return f"{self.student} → {self.school_class} ({self.status})"


# ─────────────────────────────────────────────
# CURRICULUM DOWNLOADS  (Students & Parents)
# ─────────────────────────────────────────────

class CurriculumDownload(models.Model):
    """Tracks every curriculum download by a user."""

    user        = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='curriculum_downloads')
    curriculum  = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='downloads')
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-downloaded_at']

    def __str__(self):
        return f"{self.user} downloaded {self.curriculum} at {self.downloaded_at:%Y-%m-%d %H:%M}"


# ─────────────────────────────────────────────
# TRIAL BOOKING  (Parents)
# ─────────────────────────────────────────────

class TrialBooking(models.Model):
    """A parent books a trial class for their child."""

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    parent        = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='trial_bookings',
        limit_choices_to={'role': CustomUser.PARENT},
    )
    school_class  = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='trial_bookings')
    child_name    = models.CharField(max_length=200)
    child_age     = models.PositiveSmallIntegerField(null=True, blank=True)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message       = models.TextField(blank=True)
    booked_at     = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trial: {self.parent} for {self.child_name} → {self.school_class} on {self.preferred_date}"


# ─────────────────────────────────────────────
# CONSULTATION  (Parents)
# ─────────────────────────────────────────────

class Consultation(models.Model):
    """A parent schedules a consultation with the school."""

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    TOPIC_CHOICES = [
        ('admissions',  'Admissions'),
        ('curriculum',  'Curriculum'),
        ('progress',    'Student Progress'),
        ('fees',        'Fees & Payment'),
        ('other',       'Other'),
    ]

    parent         = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='consultations',
        limit_choices_to={'role': CustomUser.PARENT},
    )
    topic          = models.CharField(max_length=20, choices=TOPIC_CHOICES, default='admissions')
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message        = models.TextField(blank=True)
    admin_notes    = models.TextField(blank=True)
    scheduled_at   = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consultation: {self.parent} – {self.get_topic_display()} on {self.preferred_date}"
    
    
    
class GalleryItem(models.Model):
    TYPE_CHOICES = [('image', 'Image'), ('video', 'Video')]
    CATEGORY_CHOICES = [
        ('event',     'Event'),
        ('workshop',  'Workshop'),
        ('community', 'Community'),
    ]
 
    title     = models.CharField(max_length=200)
    media     = models.FileField(upload_to='gallery/')
    thumbnail = models.ImageField(upload_to='gallery/thumbs/', blank=True, null=True)
    type      = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category  = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date      = models.DateField()
    caption   = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['-date', '-uploaded_at']
 
    def __str__(self):
        return f"{self.title} ({self.type})"
 
    def is_video(self):
        return self.type == 'video'