from django.contrib import admin
from django.urls import path, include
import whatsappsend.views
from whatsappsend import views

app_name = "whatsappsend"
urlpatterns = [
    path('', views.index, name='index'),
    path('sendbystring/', views.read_whatsapp, name='read_whatsapp'),
    path('sendattached/', views.send_attached, name='send_attached'),
    path('bulk_text/', views.bulk_text, name='bulk_text'),
    path('unread_response/', views.response_to_unread, name='unread_response'),

]