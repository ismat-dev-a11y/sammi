from rest_framework import serializers
from .models import Project, ProjectStep, ProjectFeature
from apps.courses.models import Technology
from drf_spectacular.utils import extend_schema_field
# from drf_spectacular.types import OpenApiTypes
from utils.minio_client import upload_to_minio
from moviepy.video.io.VideoFileClip import VideoFileClip
import tempfile
import os
from utils.minio_client import upload_project_video_to_minio, get_minio_url


class TechnologySerializers(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Technology
        fields = ['id', 'category', 'category_display', 'label', 'value']
        read_only_fields = ['id']

# serializers.py

class ProjectStepSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField(read_only=True)
    video = serializers.FileField(
        write_only=True,
        required=False,
        help_text="Upload step video (MP4, etc.)"
    )

    class Meta:
        model = ProjectStep
        fields = [
            'id', 'project', 'title', 'video', 'video_url',
            'duration', 'order',
        ]
        read_only_fields = ['id', 'video_url']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_video_url(self, obj):
        if obj.video_key:
            if obj.video_url:
                return obj.video_url
            return f"http://84.247.165.177:9000/sammi-media/{obj.video_key}"
        return None

    def create(self, validated_data):
        video_file = validated_data.pop('video', None)
        step = ProjectStep(**validated_data)

        if video_file:
            project = validated_data['project']
            order   = validated_data.get('order', 0)

            step.duration  = self._get_video_duration(video_file)
            step.video_key = upload_project_video_to_minio(video_file, project.slug, order)
            step.video_url = get_minio_url(step.video_key)

        step.save()
        return step

    def update(self, instance, validated_data):
        video_file = validated_data.pop('video', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if video_file:
            project = instance.project
            video_key = f"projects/videos/{project.slug}/step-{instance.order}.mp4"
            instance.video_key = upload_to_minio(video_file, video_key)
            instance.video_url = f"http://84.247.165.177:9000/sammi-media/{instance.video_key}"

        instance.save()
        return instance


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating projects - handles optional image properly"""
    image = serializers.ImageField(
        required=False,
        help_text="Upload new project image (JPEG, PNG, etc.) - leave empty to keep current image"
    )
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'title', 'description', 'image', 'image_url',
            'difficulty', 'github_url', 'demo_url',
            'technologies'
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except (ValueError, AttributeError):
                return None
        return None

    def validate_image(self, value):
        """Custom validation to handle optional image field"""
        # If no file is provided, return None to skip image update
        if value is None or value == '':
            return None
        return value

    def update(self, instance, validated_data):
        """Handle image update properly - only update if new image is provided"""
        image = validated_data.pop('image', None)
        technologies = validated_data.pop('technologies', None)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle many-to-many technologies field separately
        if technologies is not None:
            instance.technologies.set(technologies)

        # Only update image if a new one is provided (not None or empty)
        if image is not None and image != '':
            instance.image = image

        instance.save()
        return instance

    def partial_update(self, instance, validated_data):
        """Handle partial updates - same logic as full update"""
        return self.update(instance, validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for project list view for users"""
    image_url = serializers.SerializerMethodField(read_only=True)
    technologies = TechnologySerializers(many=True, read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    total_steps = serializers.IntegerField(read_only=True)
    total_duration_str = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'image_url',
            'difficulty', 'difficulty_display', 'github_url', 'demo_url',
            'technologies', 'created_at', 'total_steps', 'total_duration_str'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'total_steps', 'total_duration_str']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except (ValueError, AttributeError):
                return None
        return None


class ProjectFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFeature
        fields = ['id', 'text', 'order']


class ProjectStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStep
        fields = ['id', 'title', 'video_url', 'duration', 'order']


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single project view"""
    image_url = serializers.SerializerMethodField(read_only=True)
    technologies = TechnologySerializers(many=True, read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    total_steps = serializers.IntegerField(read_only=True)
    total_duration_str = serializers.CharField(read_only=True)
    features = ProjectFeatureSerializer(many=True, read_only=True)
    steps = ProjectStepSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'image_url',
            'difficulty', 'difficulty_display', 'github_url', 'demo_url',
            'technologies', 'created_at', 'total_steps', 'total_duration_str',
            'features', 'steps'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'total_steps', 'total_duration_str']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj):
        if obj.image:
            try:
                return obj.image.url
            except (ValueError, AttributeError):
                return None
        return None

# ProjectStep
class ProjectStepActionSerializer(serializers.ModelSerializer):
    video = serializers.FileField(write_only=True, required=False)
    video_url = serializers.SerializerMethodField(read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProjectStep
        fields = ['id', 'project', 'title', 'video', 'video_url', 'duration', 'order']
        read_only_fields = ['id', 'duration', 'video_url', 'project']

    def get_video_url(self, obj):
        if obj.video_key:
            return obj.video_url or get_minio_url(obj.video_key)
        return None

    def _get_video_duration(self, video_file) -> int:
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                for chunk in video_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            clip = VideoFileClip(tmp_path)
            duration_minutes = int(clip.duration / 60)
            clip.close()
            os.unlink(tmp_path)
            return max(duration_minutes, 1)
        except Exception:
            return 0

    def create(self, validated_data):
        video_file = validated_data.pop('video', None)
        step = ProjectStep(**validated_data)

        if video_file:
            project = validated_data['project']
            order   = validated_data.get('order', 0)

            step.duration  = self._get_video_duration(video_file)
            step.video_key = upload_project_video_to_minio(video_file, project.slug, order)  # ✅
            step.video_url = get_minio_url(step.video_key)  # ✅

        step.save()
        return step

    def update(self, instance, validated_data):
        video_file = validated_data.pop('video', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if video_file:
            instance.duration  = self._get_video_duration(video_file)
            instance.video_key = upload_project_video_to_minio(  # ✅
                video_file, instance.project.slug, instance.order
            )
            instance.video_url = get_minio_url(instance.video_key)  # ✅

        instance.save()
        return instance

class ProjectStepListSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProjectStep
        fields = ['id', 'project', 'title', 'video_url', 'duration', 'order']
        read_only_fields = ['id', 'video_url']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_video_url(self, obj):
        if obj.video_key:
            return obj.video_url or f"http://84.247.165.177:9000/sammi-media/{obj.video_key}"
        return None


class ProjectStepDetailSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProjectStep
        fields = ['id', 'project', 'title', 'video_url', 'duration', 'order']
        read_only_fields = ['id', 'video_url']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_video_url(self, obj):
        if obj.video_key:
            return obj.video_url or f"http://84.247.165.177:9000/sammi-media/{obj.video_key}"
        return None