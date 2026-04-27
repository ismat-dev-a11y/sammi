# apps/sources/serializers.py
from rest_framework import serializers
from apps.courses.models import Technology
from .models import SourceCode


class TechnologyShortSerializer(serializers.ModelSerializer):
    """Technology modeli uchun qisqa ko'rinish (nested)."""
    class Meta:
        model = Technology
        fields = ["id", "name"]  # Technology modelingizga qarab maydonlarni moslashtiring


class SourceCodeListSerializer(serializers.ModelSerializer):
    """Ro'yxat ko'rinishi uchun — yengil serializer."""
    technologies = TechnologyShortSerializer(many=True, read_only=True)

    class Meta:
        model = SourceCode
        fields = [
            "id",
            "title",
            "slug",
            "github_url",
            # "technologies",
            # "order",
            "is_published",
            "created_at",
        ]


class SourceCodeDetailSerializer(serializers.ModelSerializer):
    """Batafsil ko'rinish uchun."""
    # technologies = TechnologyShortSerializer(many=True, read_only=True)

    class Meta:
        model = SourceCode
        fields = [
            "id",
            "title",
            "slug",
            "github_url",
            # "technologies",
            # "order",
            "is_published",
            "created_at",
        ]
        read_only_fields = ["slug", "created_at"]


class SourceCodeCreateUpdateSerializer(serializers.ModelSerializer):
    """Create va Update uchun — technologies ni ID lar orqali qabul qiladi."""
    # technologies = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     queryset=Technology.objects.all(),
    #     required=False,
    # )

    class Meta:
        model = SourceCode
        fields = [
            "id",
            "title",
            # "slug",
            "github_url",
            # "technologies",
            # "order",
            # "is_published",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_github_url(self, value):
        """GitHub URL ekanligini tekshirish."""
        if "github.com" not in value:
            raise serializers.ValidationError("URL github.com domeniga tegishli bo'lishi kerak.")
        return value

    # def to_representation(self, instance):
    #     """Javobda technologies ni to'liq ko'rsatish uchun."""
    #     representation = super().to_representation(instance)
    #     representation["technologies"] = TechnologyShortSerializer(
    #         instance.technologies.all(), many=True
    #     ).data
    #     return representation