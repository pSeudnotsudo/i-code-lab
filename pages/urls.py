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
    # path('login/', views.login_view, name='login'),
    # path('register/', views.register_view, name='register'),
    
    # AUTHENTICATION
    path('auth/',views.login_view,   name='login'),
    path('auth/register/',views.register,name='register'),
    path('auth/confirm-email/<uidb64>/<token>/',views.confirm_email,name='confirm_email'),
    path('auth/confirm-sent/', lambda r: render(r, 'authentication/email_confirm_sent.html'),name='email_confirm_sent'),
    
    # DASHBOARDS
    # path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/parent/',  views.parent_dashboard,  name='parent_dashboard'),
    # path('dashboard/admin/',   views.admin_dashboard,   name='admin_dashboard'),
    
    # PUBLIC URLS
    
    path('programs/', views.programs, name='programs'),
    path('about/', views.about, name='about'),
    path('logout/', views.logout_view, name='logout'),
    path('pricing/', views.pricing, name='pricing'),
    
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

]