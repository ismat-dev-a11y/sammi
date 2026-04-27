from django.urls import path
from . import views

urlpatterns = [
    # Admin endpoints
    path('projects/admin/create', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/admin/<int:pk>/update', views.ProjectUpdateView.as_view(), name='project-update'),
    path('projects/admin/<int:pk>/delete', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('projects/steps/create', views.ProjectCreateView.as_view(), name='project-step-create'),
    
    # Public endpoints
    path('projects', views.ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/steps', views.ProjectStepListView.as_view(), name='project-step-list'),
    path('projects/steps/<int:pk>', views.ProjectStepDetailView.as_view(), name='project-step-detail'),
]
