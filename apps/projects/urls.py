from django.urls import path
from .views import *

urlpatterns = [
    path('projects/admin/create', ProjectCreateView.as_view(), name='project-create'),
    path('projects/admin/list', ProjectAdminListView.as_view(), name='project-admin-list'),
    path('projects/admin/<int:pk>/update', ProjectUpdateView.as_view(), name='project-update'),
    path('projects/admin/<int:pk>/delete', ProjectDeleteView.as_view(), name='project-delete'),
    # ← bu qator o'chirildi

    path('projects/<int:project_pk>/steps/',
         ProjectStepListView.as_view(), name='project-step-list'),

    path('projects/<int:project_pk>/steps/create/',
         ProjectStepView.as_view(), name='project-step-create'),

    path('projects/<int:project_pk>/steps/<int:pk>/',
         ProjectStepDetailView.as_view(), name='project-step-detail'),

    path('projects/<int:project_pk>/steps/<int:pk>/update/',
         ProjectStepUpdateView.as_view(), name='project-step-update'),

    path('projects/<int:project_pk>/steps/<int:pk>/delete/',
         ProjectStepDeleteView.as_view(), name='project-step-delete'),

    path('projects/steps/admin/list', ProjectStepAdminListView.as_view(), name='project-step-admin-list'),
]
