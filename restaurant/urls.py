from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.main, name='restaurant'),
    path(r'main/', views.main, name='main'),
    path(r'order/', views.order, name='order'),
    path(r'confirmation/', views.confirmation, name='confirmation'),

   
]
