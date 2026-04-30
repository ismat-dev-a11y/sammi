import requests
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class GitHubAuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)  # Frontend dan keladi

    def validate_code(self, code):
        # 1. code → access_token
        client_id     = settings.SOCIALACCOUNT_PROVIDERS["github"]["APP"]["client_id"]
        client_secret = settings.SOCIALACCOUNT_PROVIDERS["github"]["APP"]["secret"]

        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id":     client_id,
                "client_secret": client_secret,
                "code":          code,
            },
            headers={"Accept": "application/json"},
            timeout=10,
        )

        token_data = token_response.json()

        access_token = token_data.get("access_token")
        if not access_token:
            raise serializers.ValidationError(
                f"GitHub token olishda xato: {token_data.get('error_description', 'Noma`lum xato')}"
            )

        # 2. access_token → user info
        user_response = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept":        "application/vnd.github+json",
            },
            timeout=10,
        )

        if user_response.status_code != 200:
            raise serializers.ValidationError("GitHub foydalanuvchi ma'lumotlarini olishda xato.")

        user_data = user_response.json()

        # 3. Email alohida endpoint dan keladi (GitHub email ni yashirishi mumkin)
        if not user_data.get("email"):
            email_response = requests.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept":        "application/vnd.github+json",
                },
                timeout=10,
            )
            emails = email_response.json()

            # Primary va verified emailni olamiz
            primary_email = next(
                (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                None,
            )
            user_data["email"] = primary_email

        if not user_data.get("email"):
            raise serializers.ValidationError(
                "GitHub accountingizda verified email topilmadi."
            )

        return user_data

    def get_or_create_user(self):
        github_data   = self.validated_data["code"]
        language_code = self.validated_data.get("language_code", "en")

        email      = github_data.get("email", "")
        full_name  = github_data.get("name") or github_data.get("login", "")
        avatar_url = github_data.get("avatar_url", "")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name":     full_name,
                "avatar_url":    avatar_url,
                "language_code": language_code,
                "is_active":     True,
                "is_new_user":   True,
            },
        )

        if not created:
            update_fields = []

            if avatar_url and user.avatar_url != avatar_url:
                user.avatar_url = avatar_url
                update_fields.append("avatar_url")

            if user.is_new_user:
                user.is_new_user = False
                update_fields.append("is_new_user")

            if update_fields:
                user.save(update_fields=update_fields)

        return user, created