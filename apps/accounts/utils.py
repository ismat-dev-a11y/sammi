import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings


def generate_otp():
    return str(random.randint(100000, 999999))


def get_otp_key(email):
    return f"otp_{email.lower().strip()}"


def send_otp_email(email):
    otp = generate_otp()
    key = get_otp_key(email)

    cache.set(key, otp, timeout=300)  # 5 minut

    send_mail(
        subject="Your OTP Code",
        message=f"Your verification code is: {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,  # <--- SHU QATORNI QO'SHING
    )
    return otp


def verify_otp(email, otp):
    key = get_otp_key(email)
    cached_otp = cache.get(key)

    if cached_otp is None:
        return False

    if str(cached_otp) == str(otp):
        cache.delete(key)
        return True

    return False