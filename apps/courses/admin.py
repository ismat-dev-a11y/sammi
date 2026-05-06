from django.contrib import admin
from .models import Category, Technology, Course, Module, Lesson, Enrollment, LessonProgress, Review

admin.site.register(Category)
admin.site.register(Technology)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(LessonProgress)
admin.site.register(Review)