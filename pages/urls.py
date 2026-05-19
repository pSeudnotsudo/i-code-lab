from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from django.urls import path
from django.shortcuts import render
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    # AUTHENTICATION
    path('auth/',views.login_view,   name='login'),
    # path('auth/register/',views.register,name='register'),
    path('auth/confirm-email/<uidb64>/<token>/',views.confirm_email,name='confirm_email'),
    path('auth/confirm-sent/', lambda r: render(r, 'authentication/email_confirm_sent.html'),name='email_confirm_sent'),
    
    # ADMIN
    path('secure-control-9x7a2k-panel/',  views.icode_admin,  name='admin_dashboard'),
    path('icode-admin/create-user/',views.create_user, name='create_user'),
    path('activate/<uuid:token>/',views.activate_account,name='activate_account'),
    path('enrollment-list',  views.icode_enrollments,  name='enrollments_list'),
    path("enrollments/<int:pk>/update-status/", views.enrollment_update_status, name="enrollment_update_status"),
    path('age-brackets/',views.age_brackets,name='age_brackets'),

    path("age-brackets/store/",views.age_bracket_store,name="age_bracket_store"),
    
    path("statuses/",views.status_list,name="status_list"),
    path("statuses/store/",views.status_store,name="status_store"),
    path("statuses/<int:pk>/update/",views.status_update,name="status_update"),
    
    path("icode-admin/programs/",views.programs_list,name="programs_list"),
    path("programs/store/",views.program_store,name="program_store"),
    path("programs/<int:pk>/update/",views.program_update,name="program_update"),
    
    
    path("timelines/",views.timeline_list,name="timeline_list"),
    path("timelines/store/",views.timeline_store,name="timeline_store"),
    path("timelines/<int:pk>/update/",views.timeline_update,name="timeline_update"),
    
    # ENROLLMENT
    path("enrollments/store/", views.enrollment_store, name="enrollment_store"),
    
    # DASHBOARDS
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/parent/',  views.parent_dashboard,  name='parent_dashboard'),
    # path('dashboard/admin/',   views.admin_dashboard,   name='admin_dashboard'),
    
    # PUBLIC URLS
    
    path('programs/', views.programs, name='programs'),
    path('about/', views.about, name='about'),
    path('logout/', views.logout_view, name='logout'),
    path('pricing/', views.pricing, name='pricing'),
    path('socials/', views.socials, name='socials'),
    path('privacy-policy/', views.serve_privacy_policy, name='serve_privacy_policy'),
    # UPLOAD IMAGES $ VIDEOS.
    path('gallery/upload/', views.gallery_upload, name='gallery_upload'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='authentication/password_reset_form.html',
        email_template_name='authentication/password_reset_email.html',
        success_url='/password-reset/sent/',
    ), name='password_reset'),

    path('password-reset/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='authentication/password_reset_done.html',
    ), name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='authentication/password_reset_confirm.html',
        success_url='/password-reset/complete/',
    ), name='password_reset_confirm'),

    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='authentication/password_reset_complete.html',
    ), name='password_reset_complete'),
    # terms and conditions
    path('terms/', views.terms, name='terms'),
    # NEWSLETTER SUBSCRIBE
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/<str:email>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    
    
    
    