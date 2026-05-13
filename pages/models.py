from django.contrib.auth.models import AbstractUser
from django.db import models
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