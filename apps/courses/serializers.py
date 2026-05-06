import ast
import uuid
from django.utils.text import slugify
from rest_framework import serializers
from django.db.models import Sum, Avg
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import (
    Category,
    Technology,
    Course,
    Module,
    Lesson,
    Enrollment,
    Review,
    LessonProgress
)


class CourseCreateUpdateSerializers(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    preview_video_full_url = serializers.SerializerMethodField(read_only=True)

    image = serializers.ImageField(
        write_only=True,
        required=False,
        help_text="Upload course image (JPEG, PNG, etc.)"
    )

    preview_video = serializers.FileField(
        write_only=True,
        required=False,
        help_text="Upload course preview video (MP4, AVI, etc.)"
    )

    technologies = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Technology.objects.all(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'image',
            'image_url',
            'preview_video',
            'preview_video_full_url',
            'category',
            'technologies',
            'level',
            'price',
            'is_published',
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_preview_video_full_url(self, obj):
        return obj.preview_video.url if obj.preview_video else None

    def validate_technologies(self, value):
        if value is None:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Technologies must be a list"
            )

        return value

    def generate_unique_slug(self, title, exclude_pk=None):
        base_slug = slugify(title)
        slug = base_slug
        counter = 1

        qs = Course.objects.filter(slug=slug)

        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)

        while qs.exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

            qs = Course.objects.filter(slug=slug)

            if exclude_pk:
                qs = qs.exclude(pk=exclude_pk)

        return slug

    def create(self, validated_data):
        title = validated_data.get('title', '')
        validated_data['slug'] = self.generate_unique_slug(title)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            validated_data['slug'] = self.generate_unique_slug(
                validated_data['title'],
                exclude_pk=instance.pk
            )

        return super().update(instance, validated_data)


class CourseListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    preview_video_url_full = serializers.SerializerMethodField()
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    technologies_list = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'image_url',
            'preview_video_url_full',
            'category_name',
            'technologies_list',
            'level',
            'price',
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_preview_video_url_full(self, obj):
        return obj.preview_video.url if obj.preview_video else None

    @extend_schema_field(
        serializers.ListField(child=serializers.CharField())
    )
    def get_technologies_list(self, obj):
        return [tech.label for tech in obj.technologies.all()]


class CourseDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    preview_video_url_full = serializers.SerializerMethodField()
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    technologies_list = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    modules_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'image_url',
            'preview_video_url_full',
            'category_name',
            'technologies_list',
            'level',
            'price',
            'rating',
            'reviews_count',
            'lessons_count',
            'modules_count',
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_preview_video_url_full(self, obj):
        return obj.preview_video.url if obj.preview_video else None

    @extend_schema_field(
        serializers.ListField(child=serializers.CharField())
    )
    def get_technologies_list(self, obj):
        return [tech.label for tech in obj.technologies.all()]

    @extend_schema_field(serializers.FloatField())
    def get_rating(self, obj):
        reviews = obj.reviews.all()

        return round(
            reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0,
            1
        )

    @extend_schema_field(serializers.IntegerField())
    def get_reviews_count(self, obj):
        return obj.reviews.count()

    @extend_schema_field(serializers.IntegerField())
    def get_lessons_count(self, obj):
        return obj.total_lessons

    @extend_schema_field(serializers.IntegerField())
    def get_modules_count(self, obj):
        return obj.modules.count()


class ModuleListSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source='course.title',
        read_only=True
    )

    lessons_count = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id',
            'course',
            'course_title',
            'title',
            'order',
            'lessons_count',
            'total_duration'
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_lessons_count(self, obj):
        return obj.lessons.count()

    @extend_schema_field(serializers.FloatField())
    def get_total_duration(self, obj):
        total_minutes = (
            obj.lessons.aggregate(total=Sum('duration'))['total'] or 0
        )

        return round(total_minutes / 60, 1)