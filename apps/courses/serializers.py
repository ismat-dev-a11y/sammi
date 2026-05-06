import ast
import uuid
from django.utils.text import slugify
from rest_framework import serializers
from django.db.models import Sum
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Category, Technology, Course, Module, Lesson, Enrollment, Review, LessonProgress


class CourseCreateUpdateSerializers(serializers.ModelSerializer):
    image_url              = serializers.SerializerMethodField(read_only=True)
    preview_video_full_url = serializers.SerializerMethodField(read_only=True)
    # preview_video_url      = serializers.URLField(required=False, allow_blank=True, allow_null=True, write_only=True)

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
        allow_empty=True,
        help_text="List of technology IDs (primary keys) as array: [1, 2, 3]"
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
            # 'preview_video_url',
            'preview_video_full_url',
            'category',
            'technologies',
            'level',
            'price',
            'is_published',
        ]
        # extra_kwargs = {
        #     'preview_video_url': {'write_only': True}
        # }

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except (ValueError, AttributeError):
                return None
        return None

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_preview_video_full_url(self, obj):
        if obj.preview_video:
            try:
                return obj.preview_video.url
            except (ValueError, AttributeError):
                return None
        return None

    def validate_technologies(self, value):
        """
        Validate technologies field to ensure it's a proper list of technology IDs.
        """
        if value is None:
            return []
        
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Technologies must be a list of technology IDs. Example: [1, 2, 3]"
            )
        
        # Check if all items are valid Technology objects
        for tech in value:
            if not isinstance(tech, Technology):
                raise serializers.ValidationError(
                    f"Invalid technology ID: {tech}. Must be a valid Technology primary key."
                )
        
        return value

    # ✅ Unique slug yaratish
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
    image_url              = serializers.SerializerMethodField()
    preview_video_url_full = serializers.SerializerMethodField()
    category_name          = serializers.CharField(source='category.name', read_only=True)
    technologies_list      = serializers.SerializerMethodField()

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

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_technologies_list(self, obj):
        return [tech.label for tech in obj.technologies.all()]


class CourseDetailSerializer(serializers.ModelSerializer):
    image_url              = serializers.SerializerMethodField()
    preview_video_url_full = serializers.SerializerMethodField()
    category_name          = serializers.CharField(source='category.name', read_only=True)
    technologies_list      = serializers.SerializerMethodField()
    rating                 = serializers.SerializerMethodField()
    reviews_count          = serializers.SerializerMethodField()
    lessons_count          = serializers.SerializerMethodField()
    modules_count          = serializers.SerializerMethodField()

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

    @extend_schema_field(serializers.URLField())
    def get_preview_video_url_full(self, obj):
        if obj.preview_video:
            return obj.preview_video
        return None

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_technologies_list(self, obj):
        return [tech.name for tech in obj.technologies.all()]

    @extend_schema_field(serializers.FloatField())
    def get_rating(self, obj):
        from django.db.models import Avg
        reviews = obj.reviews.all()
        return round(reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0, 1)

    @extend_schema_field(serializers.IntegerField())
    def get_reviews_count(self, obj):
        return obj.reviews.count()

    @extend_schema_field(serializers.IntegerField())
    def get_lessons_count(self, obj):
        return obj.total_lessons

    @extend_schema_field(serializers.IntegerField())
    def get_modules_count(self, obj):
        return obj.modules.count()


# Category Serializers
class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class CategoryListSerializer(serializers.ModelSerializer):
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'courses_count']

    @extend_schema_field(serializers.IntegerField())
    def get_courses_count(self, obj):
        return obj.courses.filter(is_published=True).count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    courses_count = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'courses_count', 'courses']

    @extend_schema_field(serializers.IntegerField())
    def get_courses_count(self, obj):
        return obj.courses.filter(is_published=True).count()

    @extend_schema_field(CourseListSerializer(many=True))
    def get_courses(self, obj):
        courses = obj.courses.filter(is_published=True)
        return CourseListSerializer(courses, many=True).data


# Technology Serializers
class TechnologyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'category', 'label', 'value', 'description']


class TechnologyListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = Technology
        fields = ['id', 'category', 'category_display', 'label', 'value', 'courses_count']

    @extend_schema_field(serializers.IntegerField())
    def get_courses_count(self, obj):
        return obj.courses.filter(is_published=True).count()


class TechnologyDetailSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    courses_count = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Technology
        fields = ['id', 'category', 'category_display', 'label', 'value', 'description', 'created_at', 'courses_count', 'courses']

    @extend_schema_field(serializers.IntegerField())
    def get_courses_count(self, obj):
        return obj.courses.filter(is_published=True).count()

    @extend_schema_field(CourseListSerializer(many=True))
    def get_courses(self, obj):
        courses = obj.courses.filter(is_published=True)
        return CourseListSerializer(courses, many=True).data


class TechnologyCategorySerializer(serializers.Serializer):
    """
    Serializer for returning technologies grouped by category 
    in the format requested by the user.
    """
    label = serializers.CharField()
    options = serializers.ListField(child=serializers.DictField())


# Module Serializers
class ModuleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'order']


class ModuleListSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    lessons_count = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'course', 'course_title', 'title', 'order', 'lessons_count', 'total_duration']

    @extend_schema_field(serializers.IntegerField())
    def get_lessons_count(self, obj):
        return obj.lessons.count()

    @extend_schema_field(serializers.FloatField())
    def get_total_duration(self, obj):
        total_minutes = obj.lessons.aggregate(total=models.Sum('duration'))['total'] or 0
        return round(total_minutes / 60, 1)


class ModuleDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'course', 'course_title', 'title', 'order', 'lessons']

    @extend_schema_field(serializers.ListField())
    def get_lessons(self, obj):
        return LessonListSerializer(obj.lessons.all(), many=True).data


# Lesson Serializers
class LessonCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'module', 'title', 'video_url', 'duration', 'order', 'is_preview']


class LessonListSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)
    course_title = serializers.CharField(source='module.course.title', read_only=True)
    duration_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'module', 'module_title', 'course_title', 'title', 'video_url', 
                 'duration', 'duration_formatted', 'order', 'is_preview']

    @extend_schema_field(serializers.CharField())
    def get_duration_formatted(self, obj):
        hours = obj.duration // 60
        minutes = obj.duration % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class LessonDetailSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source='module.title', read_only=True)
    course_title = serializers.CharField(source='module.course.title', read_only=True)
    duration_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'module', 'module_title', 'course_title', 'title', 'video_url', 
                 'duration', 'duration_formatted', 'order', 'is_preview']

    @extend_schema_field(serializers.CharField())
    def get_duration_formatted(self, obj):
        hours = obj.duration // 60
        minutes = obj.duration % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


# Enrollment Serializers
class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'course']

    def create(self, validated_data):
        user = self.context['request'].user
        course = validated_data['course']
        
        # Check if already enrolled
        if Enrollment.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")
        
        return Enrollment.objects.create(user=user, **validated_data)


class EnrollmentListSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_image = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_title', 'course_image', 'enrolled_at', 'progress_percentage']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_course_image(self, obj):
        return obj.course.image.url if obj.course.image else None

    @extend_schema_field(serializers.FloatField())
    def get_progress_percentage(self, obj):
        total_lessons = obj.course.total_lessons
        if total_lessons == 0:
            return 0.0
        
        completed_lessons = obj.user.lesson_progresses.filter(
            is_completed=True,
            lesson__module__course=obj.course
        ).count()
        
        return round((completed_lessons / total_lessons) * 100, 1)


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    course = CourseDetailSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'enrolled_at', 'progress_percentage', 'completed_lessons']

    @extend_schema_field(serializers.FloatField())
    def get_progress_percentage(self, obj):
        total_lessons = obj.course.total_lessons
        if total_lessons == 0:
            return 0.0
        
        completed_lessons = obj.user.lesson_progresses.filter(
            is_completed=True,
            lesson__module__course=obj.course
        ).count()
        
        return round((completed_lessons / total_lessons) * 100, 1)

    @extend_schema_field(serializers.IntegerField())
    def get_completed_lessons(self, obj):
        return obj.user.lesson_progresses.filter(
            is_completed=True,
            lesson__module__course=obj.course
        ).count()


# LessonProgress Serializers
class LessonProgressCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ['id', 'lesson', 'is_completed']

    def create(self, validated_data):
        user = self.context['request'].user
        lesson = validated_data['lesson']
        
        # Check if user is enrolled in the course
        if not Enrollment.objects.filter(user=user, course=lesson.module.course).exists():
            raise serializers.ValidationError("You must be enrolled in this course to track progress.")
        
        return LessonProgress.objects.update_or_create(
            user=user,
            lesson=lesson,
            defaults=validated_data
        )[0]


class LessonProgressListSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    module_title = serializers.CharField(source='lesson.module.title', read_only=True)
    course_title = serializers.CharField(source='lesson.module.course.title', read_only=True)

    class Meta:
        model = LessonProgress
        fields = ['id', 'lesson', 'lesson_title', 'module_title', 'course_title', 
                 'is_completed', 'watched_at']


class LessonProgressDetailSerializer(serializers.ModelSerializer):
    lesson = LessonDetailSerializer(read_only=True)

    class Meta:
        model = LessonProgress
        fields = ['id', 'lesson', 'is_completed', 'watched_at']


# Review Serializers
class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'course', 'rating', 'comment']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        course = validated_data['course']
        
        # Check if user is enrolled in the course
        if not Enrollment.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError("You must be enrolled in this course to leave a review.")
        
        return Review.objects.update_or_create(
            user=user,
            course=course,
            defaults=validated_data
        )[0]


class ReviewListSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'course', 'course_title', 'user', 'user_name', 'user_avatar', 
                 'rating', 'comment', 'created_at']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_user_avatar(self, obj):
        # Assuming user has an avatar field, adjust as needed
        return getattr(obj.user, 'avatar', None) and getattr(obj.user.avatar, 'url', None)


class ReviewDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'course', 'course_title', 'user', 'user_name', 'user_avatar', 
                 'rating', 'comment', 'created_at']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_user_avatar(self, obj):
        return getattr(obj.user, 'avatar', None) and getattr(obj.user.avatar, 'url', None)