from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'nickname', 'bio', 'email', 'avatar_url', 'language_code', 'country']
        read_only_fields = ['email']


class ChangePasswordSerializer(serializers.Serializer):
    current_password     = serializers.CharField(write_only=True)
    new_password         = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Parollar mos kelmadi."})
        return data

    def validate_current_password(self, value):
        user = self.context['request'].user
        if user.is_oauth_user:
            raise serializers.ValidationError("Google orqali kirgan foydalanuvchi parol o'zgartira olmaydi.")
        if not user.check_password(value):
            raise serializers.ValidationError("Joriy parol noto'g'ri.")
        return value