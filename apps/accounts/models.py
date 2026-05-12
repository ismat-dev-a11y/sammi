# apps/accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    # ── Oddiy user yaratish ────────────────────────────────────
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email kiritish majburiy"))

        email = self.normalize_email(email)          # EXAMPLE@Gmail.com → example@gmail.com
        extra_fields.setdefault("is_active", True)   # Yangi user darhol aktiv

        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)              # Parolni hash qilib saqlaydi
        else:
            user.set_unusable_password()             # Google user — parol yo'q

        user.save(using=self._db)
        return user

    # ── Superuser yaratish ─────────────────────────────────────
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser uchun is_staff=True bo'lishi shart"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser uchun is_superuser=True bo'lishi shart"))

        return self.create_user(email, password, **extra_fields)

    # ── Google OAuth uchun asosiy metod ───────────────────────
    def get_or_create_google_user(self, google_data: dict):

        google_id = google_data.get("sub")
        email     = self.normalize_email(google_data.get("email", ""))

        if not google_id or not email:
            raise ValueError(_("Google dan email yoki ID kelmadi"))

        # ── Holat 1 ───────────────────────────────────────────
        user = self.filter(google_id=google_id).first()
        if user:
            return user, False

        # ── Holat 2 ───────────────────────────────────────────
        user = self.filter(email=email).first()
        if user:
            # Mavjud accountga Google ni ulash
            user.google_id  = google_id
            user.avatar_url = google_data.get("picture", user.avatar_url)
            if not user.full_name:
                user.full_name = google_data.get("name", "")
            user.save(update_fields=["google_id", "avatar_url", "full_name"])
            return user, False

        # ── Holat 3 ───────────────────────────────────────────
        user = self.create_user(
            email=email,
            full_name=google_data.get("name", ""),
            avatar_url=google_data.get("picture", ""),
            google_id=google_id,
            is_new_user=True,
        )
        return user, True


# ══════════════════════════════════════════════════════════════
#  USER MODEL
# ══════════════════════════════════════════════════════════════

class User(AbstractUser):
    username = None

    # ── Asosiy fieldlar ────────────────────────────────────────
    full_name = models.CharField(_("full name"),max_length=250,blank=True,)
    nickname   = models.CharField(_("nickname"),  max_length=50,  blank=True)  
    bio        = models.TextField(_("bio"),blank=True)
    email = models.EmailField(_("email"),max_length=254,unique=True,db_index=True,error_messages={"unique": _("Bu email allaqachon ro'yxatdan o'tgan."),},)

    # ── Google OAuth ───────────────────────────────────────────
    google_id = models.CharField(_("google id"),max_length=255,unique=True,null=True,blank=True,db_index=True,    )

    # ── Profile ────────────────────────────────────────────────
    language_code = models.CharField(
        _("language"),
        max_length=10,
        default="uz",
        choices=[
            ("uz", "O'zbekcha"),
            ("ru", "Русский"),
            ("en", "English"),
        ],
    )
    avatar_url = models.URLField(_("avatar URL"),max_length=500,blank=True,help_text=_("Google profile rasmi yoki foydalanuvchi yuklaganrasm URL i"))
    country = models.CharField(_("country"),max_length=250,blank=True,)

    # ── Timestamps ─────────────────────────────────────────────
    created_at = models.DateTimeField(_("created at"),auto_now_add=True,)

    # ── Flags ──────────────────────────────────────────────────
    is_new_user = models.BooleanField(_("is new user"),default=True,help_text=_("Foydalanuvchi birinchi marta kirganida True. ""Frontend bu flagni ko'rib onboarding sahifasini ko'rsatadi. ""Keyingi kirishda False ga o'zgartiriladi."))

    # ── Manager ────────────────────────────────────────────────
    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    # ── Properties ─────────────────────────────────────────────
    @property
    def is_oauth_user(self) -> bool:
        return bool(self.google_id)

    # ── Meta ───────────────────────────────────────────────────
    class Meta:
        db_table            = "users"
        verbose_name        = _("user")
        verbose_name_plural = _("users")
        ordering            = ["-created_at"]

    def __str__(self):
        return self.full_name or self.email

# Contact Us

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='Ism')
    email = models.EmailField(verbose_name='email')
    message = models.TextField(verbose_name='Text')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.name} - {self.email}"

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    date = models.DateField(auto_now_add=True)  # Faqat kunni saqlaydi
    count = models.PositiveIntegerField(default=0)  # Shu kundagi harakatlar soni

    class Meta:
        unique_together = ('user', 'date')  # Bir kunda bir foydalanuvchi uchun bitta qator
        verbose_name = "Foydalanuvchi faolligi"
        verbose_name_plural = "Foydalanuvchilar faolligi"

    def __str__(self):
        return f"{self.user.email} - {self.date}: {self.count}"