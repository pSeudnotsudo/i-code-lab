from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('courses/', views.courses, name='courses'),
    path('about/', views.about, name='about'),
    path('blog/', views.index, name='blog'),
    path('membership/', views.membership, name='membership'),
     path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='your_app/password_reset_form.html',
        email_template_name='your_app/password_reset_email.html',
        success_url='/password-reset/sent/',
    ), name='password_reset'),

    path('password-reset/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='your_app/password_reset_done.html',
    ), name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='your_app/password_reset_confirm.html',
        success_url='/password-reset/complete/',
    ), name='password_reset_confirm'),

    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='your_app/password_reset_complete.html',
    ), name='password_reset_complete'),
  
]