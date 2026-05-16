from django.urls import path
from .views import (
    CourseCreateView, CourseListView, CourseUpdateView, CourseDetailView, CourseDeleteView,
    CategoryCreateView, CategoryListView, CategoryUpdateView, CategoryDetailView, CategoryDeleteView,
    TechnologyCreateView, TechnologyListView, TechnologyUpdateView, TechnologyDetailView, TechnologyDeleteView, ModuleCreateView, ModuleListView, ModuleUpdateView, ModuleDetailView, ModuleDeleteView,
    LessonCreateView, LessonListView, LessonUpdateView, LessonDetailView, LessonDeleteView,
    LessonProgressCreateView, LessonProgressListView, LessonProgressDetailView, LessonProgressUpdateView,
    ReviewCreateView, ReviewListView, ReviewUpdateView, ReviewDetailView, ReviewDeleteView, EnrollmentCreateView, EnrollmentListView, EnrollmentDetailView, EnrollmentDeleteView
)

urlpatterns = [
    # Course URLs (existing)
    path('course/', CourseCreateView.as_view()),
    path('course/list', CourseListView.as_view()),
    path('course/<int:pk>/', CourseUpdateView.as_view()),
    path('course/detail/<int:pk>/', CourseDetailView.as_view()),
    path('course/delete/<int:pk>/', CourseDeleteView.as_view()),
    
    # Category URLs
    path('category/', CategoryCreateView.as_view()),
    path('category/list', CategoryListView.as_view()),
    path('category/<int:pk>/', CategoryUpdateView.as_view()),
    path('category/detail/<int:pk>/', CategoryDetailView.as_view()),
    path('category/delete/<int:pk>/', CategoryDeleteView.as_view()),
    
    # Technology URLs
    path('technology/', TechnologyCreateView.as_view()),
    path('technology/list', TechnologyListView.as_view()),
    path('technology/<int:pk>/', TechnologyUpdateView.as_view()),
    path('technology/detail/<int:pk>/', TechnologyDetailView.as_view()),
    path('technology/delete/<int:pk>/', TechnologyDeleteView.as_view()),
    # path('technology/grouped', TechnologyGroupedView.as_view()),
    
    # Module URLs
    path('modules/', ModuleCreateView.as_view()),
    path('modules/list', ModuleListView.as_view()),
    path('modules/<int:pk>/', ModuleUpdateView.as_view()),
    path('modules/detail/<int:pk>/', ModuleDetailView.as_view()),
    path('modules/delete/<int:pk>/', ModuleDeleteView.as_view()),
    
    # Lesson URLs
    path('lessons/', LessonCreateView.as_view()),
    path('lessons/list', LessonListView.as_view()),
    path('lessons/<int:pk>/', LessonUpdateView.as_view()),
    path('lessons/detail/<int:pk>/', LessonDetailView.as_view()),
    path('lessons/delete/<int:pk>/', LessonDeleteView.as_view()),
    
    # Enrollment URLs
    path('enrollment/', EnrollmentCreateView.as_view()),
    path('enrollment/list', EnrollmentListView.as_view()),
    path('enrollment/<int:pk>/', EnrollmentDetailView.as_view()),
    path('enrollment/delete/<int:pk>/', EnrollmentDeleteView.as_view()),
    
    # LessonProgress URLs
    path('lesson-progress/', LessonProgressCreateView.as_view()),
    path('lesson-progress/list', LessonProgressListView.as_view()),
    path('lesson-progress/<int:pk>/', LessonProgressDetailView.as_view()),
    path('lesson-progress/<int:pk>/', LessonProgressUpdateView.as_view()),
    
    # Review URLs
    path('review/', ReviewCreateView.as_view()),
    path('review/list', ReviewListView.as_view()),
    path('review/<int:pk>/', ReviewUpdateView.as_view()),
    path('review/detail/<int:pk>/', ReviewDetailView.as_view()),
    path('review/delete/<int:pk>/', ReviewDeleteView.as_view()),
]
