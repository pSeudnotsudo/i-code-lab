

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('programs/', views.programs, name='programs'),
    # path('login/', views.login, name='login'),
    # path('register/', views.register, name='register'),
    # path('courses/', views.courses, name='courses'),
    # path('about/', views.about, name='about'),
    # path('services/', views.services, name='services'),
    
  
]