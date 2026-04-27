from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from .models import User




class GoogleAuthSerializer(serializers.Serializer):
    token         = serializers.CharField(required=True)


    def validate_token(self, token):
        client_id = settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"]

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                client_id,
                clock_skew_in_seconds=10,
            )
        except ValueError as e:
            raise serializers.ValidationError(f"Token yaroqsiz: {e}")

        if idinfo.get("aud") != client_id:
            raise serializers.ValidationError("Token boshqa ilovaga tegishli.")

        return idinfo

    def get_or_create_user(self):
        idinfo        = self.validated_data["token"]
        language_code = self.validated_data.get("language_code", "en")

        email      = idinfo.get("email", "")
        full_name  = idinfo.get("name", "")
        avatar_url = idinfo.get("picture", "")

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


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password_confirm', 'country', 'language_code']

    def validate_email(self, value):
        """Email uniqueness validation"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return value

    def validate(self, attrs):
        """Password confirmation validation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Parollar mos kelmadi.")
        return attrs

    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            country=validated_data.get('country', ''),
            language_code=validated_data.get('language_code', 'uz'),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """User login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate credentials"""
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                              username=email, password=password)
            
            if not user:
                raise serializers.ValidationError("Email yoki parol noto'g'ri.")
            
            if not user.is_active:
                raise serializers.ValidationError("Hisob faol emas.")
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Email va parol kiritish shart.")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model        = User
        fields       = ["id", "email", "full_name", "avatar_url", "country", "language_code", "created_at", "is_new_user"]
        read_only_fields = ["id", "email", "created_at", "is_new_user"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """PATCH /auth/me/ uchun"""
    class Meta:
        model  = User
        fields = ["full_name", "avatar_url", "country", "language_code"]
    