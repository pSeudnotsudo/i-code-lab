from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('/login', views.login, name='login'),
    path('/register', views.register, name='register'),
    path('/courses', views.courses, name='courses'),
    path('/about', views.about, name='about'),
    path('/blog', views.index, name='blog'),
    path('/membership', views.membership, name='membership'),
  
]