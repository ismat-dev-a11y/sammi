# apps/sources/admin.py
from django.contrib import admin
from .models import SourceCode


@admin.register(SourceCode)
class SourceCodeAdmin(admin.ModelAdmin):
    list_display = ["title", "order", "is_published", "created_at"]
    list_filter = ["is_published", "technologies"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["technologies"]
    list_editable = ["order", "is_published"]