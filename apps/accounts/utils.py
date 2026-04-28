import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email):
    otp = generate_otp()
    cache.set(email, otp, timeout=120)

    send_mail(
        subject="Your OTP Code",
        message=f"Your verification code is: {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )
    return otp


def verify_otp(email, otp):
    cached_otp = cache.get(email)

    if cached_otp is None:
        return False

    if cached_otp == otp:
        cache.delete(email)
        return True

    return False