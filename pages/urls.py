

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from . import admin_views   
from . import authentication_views   

# app_name = "pages"

urlpatterns = [

    # ─────────────────────────────────────────────
    #  PUBLIC PAGES
    # ─────────────────────────────────────────────
    path("", views.index, name="index"),
    path("courses/<slug:slug>/", views.course_detail, name="course_detail"),
    path("programs/", views.programs, name="programs"),
    path('testimonials/submit/', views.submit_testimonial, name='submit_testimonial'),

    # ─────────────────────────────────────────────
    #  PUBLIC AJAX ENDPOINTS
    # ─────────────────────────────────────────────
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    
    
    # ─────────────────────────────────────────────
    #  AUTH
    # ─────────────────────────────────────────────
    path("icode/login/",  authentication_views.icode_login,  name="login"),
    path("icode/logout/", authentication_views.admin_logout, name="logout"),

    # ─────────────────────────────────────────────
    #  ADMIN DASHBOARD  (protect with login_required / staff_required)
    # ─────────────────────────────────────────────
    path("icode/", admin_views.dashboard, name="icode_dashboard"),

    # ── Dashboard stats (read-only summary JSON) ──
    path("admin-ajax/stats-summary/", admin_views.stats_summary, name="admin_stats_summary"),

    # ── Courses ──────────────────────────────────
    path("admin-ajax/courses/", admin_views.course_list, name="admin_course_list"),
    path("admin-ajax/courses/add/", admin_views.course_add, name="admin_course_add"),
    path("admin-ajax/courses/<int:pk>/delete/", admin_views.course_delete, name="admin_course_delete"),

    # ── Scheduled Classes ─────────────────────────
    path("admin-ajax/scheduled/", admin_views.scheduled_list, name="admin_scheduled_list"),
    path("admin-ajax/scheduled/add/", admin_views.scheduled_add, name="admin_scheduled_add"),
    path("admin-ajax/scheduled/<int:pk>/delete/", admin_views.scheduled_delete, name="admin_scheduled_delete"),

    # ── Stats Strip ───────────────────────────────
    path("admin-ajax/stats/", admin_views.stat_list, name="admin_stat_list"),
    path("admin-ajax/stats/add/", admin_views.stat_add, name="admin_stat_add"),
    path("admin-ajax/stats/<int:pk>/delete/", admin_views.stat_delete, name="admin_stat_delete"),

    # ── Enrollments ───────────────────────────────
    path("admin-ajax/enrollments/", admin_views.enrollment_list, name="admin_enrollment_list"),
    
    # Enroll to course
    path('courses/<int:course_pk>/enroll/', views.enroll_ajax, name='enroll_ajax'),

    # ── Reviews ───────────────────────────────────
    path("admin-ajax/reviews/", admin_views.review_list, name="admin_review_list"),
    path("admin-ajax/reviews/<int:pk>/approve/", admin_views.review_approve, name="admin_review_approve"),
    path("admin-ajax/reviews/<int:pk>/delete/", admin_views.review_delete, name="admin_review_delete"),

    # ── Testimonials ──────────────────────────────
    path("admin-ajax/testimonials/", admin_views.testimonial_list, name="admin_testimonial_list"),
    path("admin-ajax/testimonials/add/", admin_views.testimonial_add, name="admin_testimonial_add"),
    path("admin-ajax/testimonials/<int:pk>/delete/", admin_views.testimonial_delete, name="admin_testimonial_delete"),

    # ── Newsletter ────────────────────────────────
    path("admin-ajax/newsletter/", admin_views.newsletter_list, name="admin_newsletter_list"),
    path("admin-ajax/newsletter/<int:pk>/delete/", admin_views.newsletter_delete, name="admin_newsletter_delete"),

    # ── Site Settings ─────────────────────────────
    path("admin-ajax/settings/", admin_views.settings_get, name="admin_settings_get"),
    path("admin-ajax/settings/update/", admin_views.settings_update, name="admin_settings_update"),
]


    
    
    
    


# urlpatterns = [
#     path('', views.index, name='index'),
#     path('programs/', views.programs, name='programs'),
#     # path('login/', views.login, name='login'),
#     # path('register/', views.register, name='register'),
#     # path('courses/', views.courses, name='courses'),
#     # path('about/', views.about, name='about'),
#     # path('services/', views.services, name='services'),
    
  
# ]