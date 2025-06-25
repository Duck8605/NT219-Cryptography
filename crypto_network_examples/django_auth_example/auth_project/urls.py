"""
URL Configuration for auth_project
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from auth_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('setup-otp/', views.setup_otp, name='setup_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
]
