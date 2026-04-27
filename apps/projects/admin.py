from django.contrib import admin
from .models import Project, ProjectStep

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(ProjectStep)
class ProjectStepAdmin(admin.ModelAdmin):
    list_display = ['title', 'project']
    list_filter = ['project']
    search_fields = ['title']
    ordering = ['project', 'order']