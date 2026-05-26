from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
from django.utils.text import slugify

# age Brackets
class AgeBracket(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

# ENROLLMENT STATUS
class EnrollmentStatus(models.Model):
    name = models.CharField(max_length=50)   # e.g. Pending
    code = models.CharField(max_length=30, unique=True)  # pending
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name
 
# Programs
class Program(models.Model):
    # ── Core identity ─────────────────────────────────────────────────────
    name  = models.CharField(max_length=100)
    code  = models.CharField(max_length=50, unique=True)
    slug  = models.SlugField(max_length=120, unique=True, blank=True)

    level = models.ForeignKey(
        'Level',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='programs',
    )
    duration_weeks = models.PositiveIntegerField(null=True, blank=True)
    total_hours    = models.PositiveIntegerField(null=True, blank=True)
    term_fee       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fee_currency   = models.CharField(max_length=10, default='KES')
    # age_range      = models.CharField(max_length=40, blank=True)
    age_range = models.ForeignKey(
    'AgeBracket',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='programs',
)

    # ── Hero section ──────────────────────────────────────────────────────
    description = models.TextField(blank=True)
    hero_copy   = models.TextField(blank=True)

    # ── Bullet lists ──────────────────────────────────────────────────────
    what_they_build   = models.JSONField(default=list, blank=True)
    learning_outcomes = models.JSONField(default=list, blank=True)

    # ── Certificate ───────────────────────────────────────────────────────
    certificate_name = models.CharField(
        max_length=150,
        default='i-CODE Certificate of Completion',
        blank=True,
    )

    # ── SEO ───────────────────────────────────────────────────────────────
    meta_description = models.TextField(blank=True)

    # ── Admin / ordering ──────────────────────────────────────────────────
    is_active = models.BooleanField(default=True)
    order     = models.IntegerField(default=0)

    # ── Reverse relations (defined on the child models) ───────────────────
    # self.weeks.all()   → ProgramWeek queryset  (related_name='weeks')
    # self.tools.all()   → ProgramTool queryset  (related_name='tools')

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('programme-detail', kwargs={'slug': self.slug})

    # ── Convenience properties ────────────────────────────────────────────
    @property
    def curriculum(self):
        """Ordered curriculum weeks. Use in templates as program.curriculum"""
        return self.weeks.all()

    @property
    def tools_by_type(self):
        """
        Returns tools grouped by their ToolType, e.g.:
        [
            { 'type': <ToolType: Hardware>, 'items': [<ProgramTool>, ...] },
            { 'type': <ToolType: Software>, 'items': [<ProgramTool>, ...] },
        ]
        """
        from itertools import groupby
        grouped = []
        tools = self.tools.select_related('tool_type').order_by('tool_type__order', 'order')
        for tool_type, items in groupby(tools, key=lambda t: t.tool_type):
            grouped.append({'type': tool_type, 'items': list(items)})
        return grouped

    @property
    def fee_display(self):
        """e.g. 'KES 65,000 per term'"""
        if self.term_fee is None:
            return ''
        return f"{self.fee_currency} {self.term_fee:,.0f} per term"

    def __str__(self):
        return self.name
# Levels

class Level(models.Model):
    name  = models.CharField(max_length=50, unique=True)  # "Beginner"
    slug  = models.SlugField(max_length=50, unique=True)  # "beginner"
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class ToolType(models.Model):
    name  = models.CharField(max_length=50, unique=True)  # "Hardware"
    slug  = models.SlugField(max_length=50, unique=True)  # "hardware"
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name





class ProgramTool(models.Model):
    program   = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='tools')
    name      = models.CharField(max_length=100)
    tool_type = models.ForeignKey(
        ToolType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tools',
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name



    
class RegistrationTimeline(models.Model):
    title = models.CharField(max_length=100)  # Immediately, Within 1 week, etc
    code = models.CharField(max_length=50, unique=True)

    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    age_bracket = models.ForeignKey(AgeBracket, on_delete=models.PROTECT)
    status = models.ForeignKey(EnrollmentStatus, on_delete=models.PROTECT)

    programs = models.ManyToManyField(Program)

    other_interest = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    

    preferred_registration_date = models.DateField(
        blank=True,
        null=True
    )

    registration_timeline = models.ForeignKey(
        RegistrationTimeline,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    preferred_start_date = models.DateField(
        blank=True,
        null=True
    )

    custom_course_interest = models.CharField(
        max_length=3,
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name



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
    
    
# USER MODEL
class CustomUser(AbstractUser):
    STUDENT = 'student'
    PARENT  = 'parent'
    ADMIN   = 'admin'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (PARENT,  'Parent'),
        (ADMIN,   'Admin'),
    ]

    email      = models.EmailField(unique=True)
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    phone      = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    first_name = models.CharField(max_length=150, blank=False)
    last_name  = models.CharField(max_length=150, blank=False)

    # One-time invite link
    invite_token      = models.UUIDField(default=uuid.uuid4, unique=True)
    invite_token_used = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group', related_name='customuser_set', blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='customuser_set', blank=True,
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

class ProgramType(models.Model):
    """Fee program types — manageable from admin."""
    name  = models.CharField(max_length=100, unique=True)  # e.g. "After-School"
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class TermFee(models.Model):
    """Fee ranges shown in the Programs section and Terms & Conditions."""
    program_type = models.OneToOneField(
        ProgramType,
        on_delete=models.CASCADE,
        related_name='fee'
    )
    fee_min = models.PositiveIntegerField(help_text="Minimum fee in KES. Use same value as max for fixed price.")
    fee_max = models.PositiveIntegerField(help_text="Maximum fee in KES. Set equal to min if no range.")

    class Meta:
        ordering = ['program_type__order']

    def __str__(self):
        if self.fee_min == self.fee_max:
            return f"{self.program_type.name} — KES {self.fee_min:,}"
        return f"{self.program_type.name} — KES {self.fee_min:,} - {self.fee_max:,}"

    @property
    def display_fee(self):
        if self.fee_min == self.fee_max:
            return f"KES {self.fee_min:,}"
        return f"KES {self.fee_min:,} - {self.fee_max:,}"


class AdditionalCost(models.Model):
    """One-time fees for materials, registration, etc."""
    name   = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    note   = models.CharField(max_length=200, blank=True, null=True)
    order  = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} — KES {self.amount:,}"

    @property
    def display_amount(self):
        return f"KES {self.amount:,}"


class FeeConfig(models.Model):
    """Global fee headline figures — singleton."""
    fees_per_term_min = models.PositiveIntegerField(default=55000)
    fees_per_term_max = models.PositiveIntegerField(default=90000)
    tagline           = models.CharField(max_length=200, default="Invest in skills that last a lifetime")

    class Meta:
        verbose_name        = "Fee Configuration"
        verbose_name_plural = "Fee Configuration"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Fee Configuration"

    @property
    def display_range(self):
        return f"KES {self.fees_per_term_min:,} - {self.fees_per_term_max:,}"