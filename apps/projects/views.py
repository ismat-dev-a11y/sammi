from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.openapi import OpenApiParameter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from .models import Project, ProjectStep
from .serializers import ProjectUpdateSerializer, ProjectListSerializer, ProjectDetailSerializer, ProjectUpdateSerializer, ProjectStepActionSerializer, ProjectStepListSerializer, ProjectStepDetailSerializer, ProjectStepSerializer

class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'difficulty': {'type': 'string', 'enum': ['beginner', 'intermediate', 'advanced']},
                    'github_url': {'type': 'string', 'format': 'uri'},
                    'demo_url': {'type': 'string', 'format': 'uri'},
                    'technologies': {'type': 'array', 'items': {'type': 'integer'}},
                    'is_published': {'type': 'boolean'}
                },
                'required': ['title', 'description']
            }
        },
        responses={201: ProjectUpdateSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)

class ProjectPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProjectListView(generics.ListAPIView):
    """List view for published projects - accessible to all users"""
    serializer_class = ProjectListSerializer
    permission_classes = [AllowAny]
    pagination_class = ProjectPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'technologies']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Project.objects.filter(is_published=True).prefetch_related('technologies').annotate(
        total_steps=Count('steps'),
        total_duration=Coalesce(Sum('steps__duration'), 0)
    ).order_by('-created_at')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='difficulty',
                type=OpenApiTypes.STR,
                enum=['beginner', 'intermediate', 'advanced'],
                description='Filter by difficulty level'
            ),
            OpenApiParameter(
                name='technologies',
                type=OpenApiTypes.INT,
                description='Filter by technology ID (can be used multiple times)'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search in title and description'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                enum=['created_at', '-created_at', 'title', '-title'],
                description='Ordering field'
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                description='Page number'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description='Number of items per page'
            ),
        ],
        responses={200: ProjectListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProjectDetailView(generics.RetrieveAPIView):
    """Detail view for a single project - accessible to all users"""
    serializer_class = ProjectDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Project.objects.filter(is_published=True).prefetch_related('technologies', 'features', 'steps')

    @extend_schema(
        responses={200: ProjectDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProjectUpdateView(generics.UpdateAPIView):
    """Update view for projects - admin only"""
    serializer_class = ProjectUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Project.objects.all().prefetch_related('technologies')

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'image': {'type': 'string', 'format': 'binary', 'description': 'Upload new image - leave empty to keep current'},
                    'difficulty': {'type': 'string', 'enum': ['beginner', 'intermediate', 'advanced']},
                    'github_url': {'type': 'string', 'format': 'uri'},
                    'demo_url': {'type': 'string', 'format': 'uri'},
                    'technologies': {'type': 'array', 'items': {'type': 'integer'}},
                    'is_published': {'type': 'boolean'}
                },
            }
        },
        responses={200: ProjectUpdateSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Handle PATCH requests with optional image field"""
        # Ensure partial=True for PATCH requests
        self.serializer_class.partial = True
        return super().patch(request, *args, **kwargs)


class ProjectDeleteView(generics.DestroyAPIView):
    """Delete view for projects - admin only"""
    serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.all()

    @extend_schema(
        responses={204: None}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

# projectStep
# projectStep views

class ProjectStepView(generics.CreateAPIView):
    serializer_class = ProjectStepActionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title':    {'type': 'string'},
                    'duration': {'type': 'integer'},
                    'order':    {'type': 'integer'},
                    'video': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Upload step video (MP4, AVI, etc.)'
                    },
                },
                'required': ['title', 'order']
            }
        },
        responses={201: ProjectStepActionSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        project = get_object_or_404(Project, pk=self.kwargs.get('project_pk'))
        serializer.save(project=project)  



class ProjectStepListView(generics.ListAPIView):
    serializer_class = ProjectStepListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ProjectStep.objects.filter(
            project_id=self.kwargs.get('project_pk')
        ).order_by('order')


class ProjectStepDetailView(generics.RetrieveAPIView):
    serializer_class = ProjectStepDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ProjectStep.objects.filter(
            project_id=self.kwargs.get('project_pk')
        )


class ProjectStepUpdateView(generics.UpdateAPIView):
    serializer_class = ProjectStepActionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return ProjectStep.objects.filter(
            project_id=self.kwargs.get('project_pk')
        )

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title':    {'type': 'string'},
                    'duration': {'type': 'integer'},
                    'order':    {'type': 'integer'},
                    'video': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Upload new video - leave empty to keep current'
                    },
                }
            }
        },
        responses={200: ProjectStepActionSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ProjectStepDeleteView(generics.DestroyAPIView):
    serializer_class = ProjectStepDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProjectStep.objects.filter(
            project_id=self.kwargs.get('project_pk')
        )

    @extend_schema(responses={204: None})
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ProjectAdminListView(generics.ListAPIView):
    """Admin list view for all projects - accessible to authenticated users"""
    serializer_class = ProjectListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'technologies', 'is_published']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Project.objects.all().prefetch_related('technologies').annotate(
            total_steps=Count('steps'),
            total_duration=Coalesce(Sum('steps__duration'), 0)
        ).order_by('-created_at')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='difficulty',
                type=OpenApiTypes.STR,
                enum=['beginner', 'intermediate', 'advanced'],
                description='Filter by difficulty level'
            ),
            OpenApiParameter(
                name='technologies',
                type=OpenApiTypes.INT,
                description='Filter by technology ID (can be used multiple times)'
            ),
            OpenApiParameter(
                name='is_published',
                type=OpenApiTypes.BOOL,
                description='Filter by published status'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search in title and description'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                enum=['created_at', '-created_at', 'title', '-title'],
                description='Ordering field'
            ),
        ],
        responses={200: ProjectListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProjectStepAdminListView(generics.ListAPIView):
    """Admin list view for all project steps - accessible to authenticated users"""
    serializer_class = ProjectStepSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project']
    ordering_fields = ['order', 'project', 'created_at']
    ordering = ['project', 'order']

    def get_queryset(self):
        return ProjectStep.objects.all().select_related('project').order_by('project', 'order')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='project',
                type=OpenApiTypes.INT,
                description='Filter by project ID'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                enum=['order', '-order', 'project', '-project'],
                description='Ordering field'
            ),
        ],
        responses={200: ProjectStepSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)