from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from io import BytesIO
import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

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

    # ── Specs (FK lookups) ────────────────────────────────────────────────
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

    custom_course_interest = models.CharField(
        max_length=3,
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        blank=True,
        null=True
    )

    # ── New fields for the enrollment form ───────────────────────────────
    referral_source = models.CharField(max_length=100, blank=True, null=True)

    track = models.CharField(
        max_length=10,
        choices=[
            ('igcse', 'IGCSE / Cambridge'),
            ('cbc',   'CBC / CBE'),
            ('none',  'No preference'),
        ],
        blank=True, null=True
    )

    cohort_label = models.CharField(max_length=150, blank=True, null=True)
    # ─────────────────────────────────────────────────────────────────────

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
    INSTRUCTOR = 'instructor'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (PARENT,  'Parent'),
        (ADMIN,   'Admin'),
        (INSTRUCTOR,   'Instructor'),
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
        
        
        
# TESTIMONIALS
class Testimonial(models.Model):
    author_name = models.CharField(max_length=100)
    author_role = models.CharField(max_length=100, help_text="E.g. 'Parent of student', 'Student")
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    avatar_initials = models.CharField(
        max_length=3,
        blank=True,
        help_text="Auto-filled from name if left blank",
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if not self.avatar_initials and self.author_name:
            parts = self.author_name.strip().split()
            if len(parts) >= 2:
                self.avatar_initials = (parts[0][0] + parts[-1][0]).upper()
            else:
                self.avatar_initials = parts[0][:2].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.author_name}"
        
class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('founder',    'Founder & CEO'),
        ('instructor', 'Instructor'),
        ('lead',       'Programme Lead'),
        ('support',    'Support Staff'),
    ]

    STRIPE_CHOICES = [
        ('teal',   'Teal'),
        ('gold',   'Gold'),
        ('navy',   'Navy'),
        ('purple', 'Purple'),
    ]
    DEPT_CHOICES = [
    ('tech',      'Tech'),
    ('education', 'Education'),
    ('ops',       'Operations'),
    ('leadership','Leadership'),
    ]
    dept = models.CharField(max_length=20, choices=DEPT_CHOICES, default='tech')

    name        = models.CharField(max_length=100)
    title       = models.CharField(max_length=150)
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default='instructor')
    bio         = models.TextField()
    photo       = models.ImageField(upload_to='team/', blank=True, null=True)
    initials    = models.CharField(max_length=3, blank=True)
    stripe      = models.CharField(max_length=10, choices=STRIPE_CHOICES, default='teal')
    credentials = models.CharField(max_length=500, blank=True)
    specialisms = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order       = models.IntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        if not self.initials and self.name:
            parts = self.name.strip().split()
            if len(parts) >= 2:
                self.initials = (parts[0][0] + parts[-1][0]).upper()
            else:
                self.initials = parts[0][:2].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} — {self.title}"

    def credentials_list(self):
        return [c.strip() for c in self.credentials.split(',') if c.strip()]

    def specialisms_list(self):
        return [s.strip() for s in self.specialisms.splitlines() if s.strip()]



    # CERT
class Programme(models.Model):
    """A course / programme certificates can be issued for.
 
    Kept as its own table instead of a hardcoded choices list so new
    programme types (bootcamps, competitions, corporate training, ...) can
    be added from the admin with no code change — this is what lets the
    system grow into the "scalable digital credential platform" described
    in the brief rather than staying a one-off page.
    """
 
    class Category(models.TextChoices):
        ROBOTICS = "robotics", "Robotics"
        AI = "ai", "Artificial Intelligence"
        CODING = "coding", "Coding / Programming"
        BOOTCAMP = "bootcamp", "Bootcamp"
        COMPETITION = "competition", "Competition"
        CORPORATE = "corporate", "Corporate Training"
        OTHER = "other", "Other"
 
    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive programmes are hidden from the certificate creation form but existing certificates keep working.",
    )
 
    class Meta:
        ordering = ["name"]
        verbose_name = "Programme / Course"
 
    def __str__(self):
        return self.name
 
 
class Certificate(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
 
    class CertificateType(models.TextChoices):
        COMPLETION = "completion", "Certificate of Completion"
        ACHIEVEMENT = "achievement", "Certificate of Achievement"
        PARTICIPATION = "participation", "Certificate of Participation"
        EXCELLENCE = "excellence", "Certificate of Excellence"
 
    class AssessmentStatus(models.TextChoices):
        PASSED = "passed", "Passed"
        PENDING = "pending", "Pending"
        NOT_REQUIRED = "not_required", "Not required"
 
    class Status(models.TextChoices):
        VALID = "valid", "Valid"
        REVOKED = "revoked", "Revoked"
 
    # 1. Certificate ID — always server-generated, never user-editable.
    certificate_id = models.CharField(max_length=24, unique=True, editable=False, db_index=True)
 
    # 2. Student / participant name
    name = models.CharField("Student / participant name", max_length=150)
 
    # 3. Course / programme
    programme = models.ForeignKey(Programme, on_delete=models.PROTECT, related_name="certificates")
 
    # 4. Level
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
 
    # 5. Certificate type
    certificate_type = models.CharField(max_length=20, choices=CertificateType.choices, default=CertificateType.COMPLETION)
 
    # 6. Date of completion
    completion_date = models.DateField("Date of completion")
 
    # 7. Certificate issue date
    issue_date = models.DateField("Certificate issue date", default=timezone.localdate)
 
    # 8. Assessment / project status
    assessment_status = models.CharField(
        "Assessment / project status", max_length=20,
        choices=AssessmentStatus.choices, default=AssessmentStatus.PASSED,
    )
 
    # 9. Certificate status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.VALID)
    revoked_reason = models.CharField(max_length=255, blank=True, help_text="Internal note — never shown on the public verification page.")
    revoked_at = models.DateTimeField(null=True, blank=True)
 
    # 10. Verification date — last time this certificate was successfully looked up
    last_verified_at = models.DateTimeField(null=True, blank=True)
 
    # 11. Optional certificate URL / PDF
    certificate_pdf = models.FileField(upload_to="certificates/pdfs/", blank=True, null=True)
 
    # 12. Optional QR verification URL
    qr_code = models.ImageField(upload_to="certificates/qrcodes/", blank=True, null=True)
    verification_url = models.URLField(blank=True, editable=False)
 
    # Audit fields — support section 9's "log certificate creation and status changes"
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="certificates_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ["-issue_date", "-created_at"]
        indexes = [models.Index(fields=["certificate_id"])]
 
    def __str__(self):
        return f"{self.certificate_id} — {self.name}"
 
    # ------------------------------------------------------------------
    # Certificate ID generation — sequential per year, collision-proof
    # under concurrent admin use.
    # ------------------------------------------------------------------
    @staticmethod
    def generate_certificate_id():
        year = timezone.now().year
        prefix = f"ICODE-{year}-"
        with transaction.atomic():
            last = (
                Certificate.objects
                .select_for_update()
                .filter(certificate_id__startswith=prefix)
                .order_by("-certificate_id")
                .first()
            )
            next_seq = int(last.certificate_id.rsplit("-", 1)[-1]) + 1 if last else 1
            candidate = f"{prefix}{next_seq:06d}"
            while Certificate.objects.filter(certificate_id=candidate).exists():
                next_seq += 1
                candidate = f"{prefix}{next_seq:06d}"
            return candidate
 
    # ------------------------------------------------------------------
    # QR code
    # ------------------------------------------------------------------
    def build_verification_url(self):
        base = getattr(settings, "SITE_URL", "https://icodeailab.com").rstrip("/")
        path = reverse("certificate_verify_direct", kwargs={"certificate_id": self.certificate_id})
        return f"{base}{path}"
 
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(self.verification_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1F3A6E", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        self.qr_code.save(f"{self.certificate_id}.png", ContentFile(buffer.getvalue()), save=False)
 
    # ------------------------------------------------------------------
    # PDF certificate
    # ------------------------------------------------------------------
    def generate_pdf(self):
        from .pdf import build_certificate_pdf  # local import avoids a circular import at app load
        pdf_bytes = build_certificate_pdf(self)
        self.certificate_pdf.save(f"{self.certificate_id}.pdf", ContentFile(pdf_bytes), save=False)
 
    # ------------------------------------------------------------------
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.certificate_id:
            self.certificate_id = self.generate_certificate_id()
        if not self.verification_url:
            self.verification_url = self.build_verification_url()
        if not self.qr_code:
            self.generate_qr_code()
        if not self.certificate_pdf:
            self.generate_pdf()
        super().save(*args, **kwargs)
        if is_new:
            CertificateAuditLog.objects.create(
                certificate=self, action=CertificateAuditLog.Action.CREATED, actor=self.created_by,
            )
 
    def mark_revoked(self, actor=None, reason=""):
        self.status = self.Status.REVOKED
        self.revoked_reason = reason
        self.revoked_at = timezone.now()
        self.save(update_fields=["status", "revoked_reason", "revoked_at", "updated_at"])
        CertificateAuditLog.objects.create(
            certificate=self, action=CertificateAuditLog.Action.REVOKED, actor=actor, note=reason,
        )
 
    def mark_valid(self, actor=None):
        self.status = self.Status.VALID
        self.revoked_reason = ""
        self.revoked_at = None
        self.save(update_fields=["status", "revoked_reason", "revoked_at", "updated_at"])
        CertificateAuditLog.objects.create(
            certificate=self, action=CertificateAuditLog.Action.RESTORED, actor=actor,
        )
 
    def register_verification_hit(self):
        """Updates verification date without re-running QR/PDF generation."""
        self.last_verified_at = timezone.now()
        Certificate.objects.filter(pk=self.pk).update(last_verified_at=self.last_verified_at)
 
 
class CertificateAuditLog(models.Model):
    """Append-only trail — satisfies 'log certificate creation and status
    changes' from section 9. Not editable or deletable from the admin."""
 
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        REVOKED = "revoked", "Revoked"
        RESTORED = "restored", "Restored to valid"
        EDITED = "edited", "Edited"
 
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name="audit_log")
    action = models.CharField(max_length=10, choices=Action.choices)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit log entry"
        verbose_name_plural = "Audit log"
 
    def __str__(self):
        return f"{self.certificate.certificate_id} · {self.action} · {self.timestamp:%Y-%m-%d %H:%M}"
 
 
class VerificationAttempt(models.Model):
    """Every lookup made against the public /verify endpoint — supports
    abuse monitoring alongside rate limiting (section 9)."""
 
    certificate_id_entered = models.CharField(max_length=24)
    matched_certificate = models.ForeignKey(
        Certificate, on_delete=models.SET_NULL, null=True, blank=True, related_name="verification_attempts",
    )
    result = models.CharField(max_length=12)  
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Verification attempt"