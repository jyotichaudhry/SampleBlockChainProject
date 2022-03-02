from django.contrib import admin
from django.urls import path

from user_registration import views

urlpatterns = [
    path('', views.home),
    path('login/', views.login_view),
    path('sign_up/', views.registration),
    path('logout/', views.logout_view),
    path('forgot_password/', views.forgot_password_view),
]
