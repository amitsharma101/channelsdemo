# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('clientlist/', views.clientList, name='clientList'),
    path('<str:room_name>/', views.room, name='room'),
    path('id/<str:room_hash>/', views.client, name='client'),
]