from django.urls import path
from . import views
from django.shortcuts import redirect


def home_redirect(request):
    return redirect("dashboard")

urlpatterns = [
    path("", home_redirect, name="home"),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('followups/create/', views.followup_create, name='followup_create'),
    path('followups/<int:pk>/edit/', views.followup_edit, name='followup_edit'),
    path('followups/<int:pk>/done/', views.followup_mark_done, name='followup_done'),
    path('p/<str:token>/', views.public_followup, name='public_followup'),
]
