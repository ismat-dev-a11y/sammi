from datetime import date
from django.db import models
from .models import UserActivity

EXCLUDED_PATHS = [
    '/auth/google/',
    '/auth/github/',
    '/login/',
    '/send-otp/',
    '/verify-otp/',
    '/refresh/',
    '/activity/',
    '/admin/',
    '/contact/',
]

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Excluded path larni tekshirish
        is_excluded = any(
            request.path.startswith(path) for path in EXCLUDED_PATHS
        )

        if (
            request.user.is_authenticated
            and request.method != "GET"
            and not is_excluded
            and response.status_code < 400  # Xatolik bo'lsa hisoblamasin
        ):
            UserActivity.objects.update_or_create(
                user=request.user,
                date=date.today(),
                defaults={},
            )
            UserActivity.objects.filter(
                user=request.user,
                date=date.today()
            ).update(count=models.F('count') + 1)

        return response