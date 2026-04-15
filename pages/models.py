from django.contrib.auth.models import AbstractUser
from django.db import models

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