from django.urls import path
from .views import GoogleAuthView, SendEmailOTPView, VerifyEmailOTPView, GitHubAuthView
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path("auth/google/", GoogleAuthView.as_view(), name="google-auth"),
    path("auth/github/", GitHubAuthView.as_view(), name="github-auth"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain"),
    path('send-otp/', SendEmailOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyEmailOTPView.as_view(), name='verify-otp'),
    # path("auth/me/",     MeView.as_view(),         name="me"),
]