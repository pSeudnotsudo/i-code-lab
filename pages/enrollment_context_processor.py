

from django.urls import reverse
from django.conf import settings

from .models import *


def enrollment_modal(request):
    """
    Adds enrollment modal context to every template.
    Queries are evaluated lazily by the ORM; only the pages that
    actually render the modal will hit the DB.
    """
    url_name = getattr(settings, "ENROLLMENT_STORE_URL_NAME", "enrollment_store")

    try:
        store_url = reverse(url_name)
    except Exception:
        store_url = "/enroll/" 

    return {
        "programs":  Program.objects.filter(is_active=True).order_by("name"),
        "brackets":  AgeBracket.objects.filter(is_active=True).order_by("name"),
        "timelines": RegistrationTimeline.objects.all().order_by("name"),
        "enrollment_store_url": store_url,
    }