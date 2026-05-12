from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Course, Category, Technology, Module, Lesson, Enrollment, LessonProgress, Review
from .utils import get_technologies_by_category
from .serializers import (
    CourseCreateUpdateSerializers, CourseListSerializer, CourseDetailSerializer,
    CategoryCreateUpdateSerializer, CategoryListSerializer, CategoryDetailSerializer,
    TechnologyCreateUpdateSerializer, TechnologyListSerializer, TechnologyDetailSerializer,
    ModuleCreateUpdateSerializer, ModuleListSerializer, ModuleDetailSerializer,
    LessonCreateUpdateSerializer, LessonListSerializer, LessonDetailSerializer,
    EnrollmentCreateSerializer, EnrollmentListSerializer, EnrollmentDetailSerializer,
    LessonProgressCreateUpdateSerializer, LessonProgressListSerializer, LessonProgressDetailSerializer,
    ReviewCreateUpdateSerializer, ReviewListSerializer, ReviewDetailSerializer
)
from core.permissions import IsAdmin

class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateUpdateSerializers
    permission_classes = [IsAdmin, IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'preview_video': {'type': 'string', 'format': 'binary'},
                    # 'preview_video_url': {'type': 'string', 'format': 'uri'},
                    'category': {'type': 'integer'},
                    'technologies': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'List of technology IDs as array: [1, 2, 3]'},
                    'level': {'type': 'string', 'enum': ['beginner', 'intermediate', 'advanced']},
                    # 'language': {'type': 'string'},
                    'price': {'type': 'number'},
                    'is_published': {'type': 'boolean'}
                },
                'required': ['title', 'description', 'category']
            }
        },
        responses={201: CourseCreateUpdateSerializers}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseListSerializer
    permission_classes = []

class CourseUpdateView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateUpdateSerializers
    permission_classes = [IsAdmin, IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'preview_video': {'type': 'string', 'format': 'binary'},
                    # 'preview_video_url': {'type': 'string', 'format': 'uri'},
                    'category': {'type': 'integer'},
                    'technologies': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'List of technology IDs as array: [1, 2, 3]'},
                    'level': {'type': 'string', 'enum': ['beginner', 'intermediate', 'advanced']},
                    # 'language': {'type': 'string'},
                    'price': {'type': 'number'},
                    'is_published': {'type': 'boolean'}
                }
            }
        },
        responses={200: CourseCreateUpdateSerializers}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseDetailSerializer
    permission_classes = []

class CourseDeleteView(generics.DestroyAPIView):
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = CourseCreateUpdateSerializers


# Category Views
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer
    permission_classes = [IsAdmin, IsAuthenticated]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer
    permission_classes = []


class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer
    permission_classes = [IsAdmin, IsAuthenticated]


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    permission_classes = []


class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = CategoryCreateUpdateSerializer


# Technology Views
class TechnologyCreateView(generics.CreateAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologyCreateUpdateSerializer
    permission_classes = [IsAdmin, IsAuthenticated]


class TechnologyListView(generics.ListAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologyListSerializer
    permission_classes = []


class TechnologyUpdateView(generics.UpdateAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologyCreateUpdateSerializer
    permission_classes = [IsAdmin, IsAuthenticated]


class TechnologyDetailView(generics.RetrieveAPIView):
    queryset = Technology.objects.all()
    serializer_class = TechnologyDetailSerializer
    permission_classes = []


class TechnologyDeleteView(generics.DestroyAPIView):
    queryset = Technology.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = TechnologyCreateUpdateSerializer


class TechnologyGroupedView(generics.GenericAPIView):
    """
    Returns technologies grouped by category in the format:
    [
        {
            "label": "Frontend",
            "options": [
                {"label": "React", "value": "react"},
                {"label": "Vue", "value": "vue"}
            ]
        },
        {
            "label": "Backend",
            "options": [
                {"label": "Node.js", "value": "node"},
                {"label": "Django", "value": "django"}
            ]
        }
    ]
    """
    permission_classes = []

    @extend_schema(
        summary="Get technologies grouped by category",
        description="Returns technologies in the format with categories and options as requested",
        responses={200: {"type": "array", "items": {"type": "object", "properties": {
            "label": {"type": "string"},
            "options": {"type": "array", "items": {"type": "object", "properties": {
                "label": {"type": "string"},
                "value": {"type": "string"}
            }}}}}}
        }
    )
    def get(self, request):
        technologies = get_technologies_by_category()
        return Response(technologies)


## ============================================================
# Module Views
# ============================================================

class ModuleCreateView(generics.CreateAPIView):
    queryset           = Module.objects.select_related('course').prefetch_related('lessons')
    serializer_class   = ModuleCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class ModuleListView(generics.ListAPIView):
    queryset           = Module.objects.select_related('course').prefetch_related('lessons')
    serializer_class   = ModuleListSerializer
    permission_classes = []


class ModuleUpdateView(generics.UpdateAPIView):
    queryset           = Module.objects.select_related('course').prefetch_related('lessons')
    serializer_class   = ModuleCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class ModuleDetailView(generics.RetrieveAPIView):
    queryset           = Module.objects.select_related('course').prefetch_related('lessons')
    serializer_class   = ModuleDetailSerializer
    permission_classes = []


class ModuleDeleteView(generics.DestroyAPIView):
    queryset           = Module.objects.select_related('course')
    serializer_class   = ModuleCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# ============================================================
# Lesson Views
# ============================================================

@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'module':     {'type': 'integer'},
                'title':      {'type': 'string'},
                'video':      {'type': 'string', 'format': 'binary'},
                'duration':   {'type': 'integer'},
                'order':      {'type': 'integer'},
                'is_preview': {'type': 'boolean'},
            }
        }
    }
)
class LessonCreateView(generics.CreateAPIView):
    queryset           = Lesson.objects.select_related('module__course')
    serializer_class   = LessonCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes     = [MultiPartParser, FormParser]


class LessonListView(generics.ListAPIView):
    queryset           = Lesson.objects.select_related('module__course')
    serializer_class   = LessonListSerializer
    permission_classes = []


@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'module':     {'type': 'integer'},
                'title':      {'type': 'string'},
                'video':      {'type': 'string', 'format': 'binary'},
                'duration':   {'type': 'integer'},
                'order':      {'type': 'integer'},
                'is_preview': {'type': 'boolean'},
            }
        }
    }
)
class LessonUpdateView(generics.UpdateAPIView):
    queryset           = Lesson.objects.select_related('module__course')
    serializer_class   = LessonCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes     = [MultiPartParser, FormParser]  # ← qo'shildi


class LessonDetailView(generics.RetrieveAPIView):
    queryset           = Lesson.objects.select_related('module__course')
    serializer_class   = LessonDetailSerializer
    permission_classes = []


class LessonDeleteView(generics.DestroyAPIView):
    queryset           = Lesson.objects.select_related('module__course')
    serializer_class   = LessonCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

# Enrollment Views
class EnrollmentCreateView(generics.CreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentCreateSerializer
    permission_classes = [IsAuthenticated]


class EnrollmentListView(generics.ListAPIView):
    serializer_class = EnrollmentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Enrollment.objects.none()
        return Enrollment.objects.filter(user=self.request.user)


class EnrollmentDetailView(generics.RetrieveAPIView):
    serializer_class = EnrollmentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Enrollment.objects.none()
        return Enrollment.objects.filter(user=self.request.user)


class EnrollmentDeleteView(generics.DestroyAPIView):
    serializer_class = EnrollmentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Enrollment.objects.none()
        return Enrollment.objects.filter(user=self.request.user)


# LessonProgress Views
class LessonProgressCreateView(generics.CreateAPIView):
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


class LessonProgressListView(generics.ListAPIView):
    serializer_class = LessonProgressListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LessonProgress.objects.none()
        return LessonProgress.objects.filter(user=self.request.user)


class LessonProgressDetailView(generics.RetrieveAPIView):
    serializer_class = LessonProgressDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LessonProgress.objects.none()
        return LessonProgress.objects.filter(user=self.request.user)


class LessonProgressUpdateView(generics.UpdateAPIView):
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


# Review Views
class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


class ReviewListView(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer
    permission_classes = []


class ReviewUpdateView(generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        return Review.objects.filter(user=self.request.user)


class ReviewDetailView(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = []


class ReviewDeleteView(generics.DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        return Review.objects.filter(user=self.request.user)