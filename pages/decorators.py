from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

STAFF_ROLES = {"admin", "instructor"}


def certificate_staff_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.is_staff or getattr(user, "role", None) in STAFF_ROLES:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You don't have permission to manage certificates.")
    return _wrapped