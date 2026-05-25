

from django.urls import reverse
from django.conf import settings

from .models import *


def enrollment_data(request):
    return {
        'programs':  Program.objects.filter(is_active=True),
        'brackets':  AgeBracket.objects.all(),
        'timelines': RegistrationTimeline.objects.all(),
    }