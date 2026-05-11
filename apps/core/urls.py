from django.urls import path
from .views import ProfileView, ChangePasswordView

urlpatterns = [
    path('settings/profile/',         ProfileView.as_view(),        name='profile'),
    path('settings/change-password/', ChangePasswordView.as_view(), name='change-password'),
]