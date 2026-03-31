"""
auth_views.py
~~~~~~~~~~~~~
Login / logout views for the I-code admin panel.
"""

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse


@require_http_methods(["GET", "POST"])
def icode_login(request):
    # Already logged-in staff → skip straight to dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("icode_dashboard")

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is None:
            if is_ajax:
                return JsonResponse({"status": "error", "error": "Invalid username or password."}, status=401)
            return render(request, "admin/icode/login.html", {
                "error_message": "Invalid username or password.",
                "username": username,
            })

        if not user.is_staff:
            if is_ajax:
                return JsonResponse({"status": "error", "error": "You do not have staff access."}, status=403)
            return render(request, "admin/icode/login.html", {
                "error_message": "Your account does not have admin access.",
                "username": username,
            })

        login(request, user)

        next_url = request.POST.get("next") or request.GET.get("next") or "icode_dashboard"

        if is_ajax:
            return JsonResponse({"status": "ok", "redirect": next_url})

        return redirect(next_url)

    return render(request, "admin/icode/login.html")


@require_http_methods(["GET", "POST"])
def admin_logout(request):
    logout(request)
    return redirect("login")