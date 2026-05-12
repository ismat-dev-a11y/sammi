from django.urls import path
from .views import GoogleAuthView, SendEmailOTPView, VerifyEmailOTPView, GitHubAuthView, ContactMessageAPiView, ContactMessageListView, UserActivityView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    path("auth/google/", csrf_exempt(GoogleAuthView.as_view()), name="google-auth"),
    path("auth/github/", csrf_exempt(GitHubAuthView.as_view()), name="github-auth"),
    path('contact/', ContactMessageAPiView.as_view()),
    path('contact/list/', ContactMessageListView.as_view()),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain"),
    path('send-otp/', SendEmailOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyEmailOTPView.as_view(), name='verify-otp'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('activity/', UserActivityView.as_view(), name='user-activity'),
    # path("auth/me/",     MeView.as_view(),         name="me"),
]