from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, ContactMessage
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
  list_display=['email']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'message', 'created_at']