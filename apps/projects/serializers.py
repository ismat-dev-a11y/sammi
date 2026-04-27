from rest_framework import serializers
from .models import Project, ProjectStep, ProjectFeature
from apps.courses.models import Technology
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class TechnologySerializers(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name']
        read_only_fields = ['id']
        
class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        write_only=True, 
        required=False,
        help_text="Upload project image (JPEG, PNG, etc.)"
    )
    image_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'image', 'image_url',
            'difficulty', 'github_url', 'demo_url', 
            'technologies', 'is_published'
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
            'technologies', 'is_published'
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
            'features', 'steps', 'is_published'
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
    video = serializers.FileField(
        write_only=True,
        required=False,
        help_text="Upload step video (MP4, AVI, etc.)"
    )
    video_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProjectStep
        fields = ['id', 'title', 'video', 'video_url', 'duration', 'order']
        read_only_fields = ['id', 'video_url']

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_video_url(self, obj):
        return obj.video_url if obj.video_url else None

class ProjectStepListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStep
        fields = ['id', 'project', 'title', 'video_url', 'duration', 'order']
        read_only_fields = ['id', 'video_url']

class ProjectStepDetailSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ProjectStep
        fields = ['id', 'title', 'video_url', 'duration', 'order']
        read_only_fields = ['id', 'video_url']
    
    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_video_url(self, obj):
        return obj.video_url if obj.video_url else None