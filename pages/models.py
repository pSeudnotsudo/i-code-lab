from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

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
    name        = models.CharField(max_length=100)
    code        = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    # icon        = models.CharField(max_length=10, default='💡')   # emoji icon
    age_range   = models.CharField(max_length=30, blank=True, null=True)  # e.g. "Ages 12+"

    is_active   = models.BooleanField(default=True)
    order       = models.IntegerField(default=0)

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