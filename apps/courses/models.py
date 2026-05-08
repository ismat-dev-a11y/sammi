from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
    

class Technology(models.Model):
    CATEGORY_CHOICES = [
        ("frontend", "Frontend"),
        ("backend", "Backend"),
        ("database", "Database"),
        ("devops", "DevOps"),
        ("mobile", "Mobile"),
        ("other", "Other"),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    label = models.CharField(max_length=100, blank=True, default='')
    value = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()}: {self.label}"

    class Meta:
        verbose_name_plural = "Technologies"
        unique_together = ("category", "label")
        ordering = ["category", "label"]


class Course(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Boshlang'ich"),
        ("intermediate", "O'rta"),
        ("advanced", "Yuqori"),
    ]
    LANGUAGE_CHOICES = [
        ("uz", "O'zbekcha"),
        ("ru", "Русский"),
        ("en", "English"),
    ]

    title             = models.CharField(max_length=255)
    slug              = models.SlugField(unique=True, blank=True)
    description       = models.TextField()
    image             = models.ImageField(upload_to="courses/images/")
    preview_video     = models.FileField(upload_to="courses/videos/", blank=True, null=True)
    category          = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    technologies      = models.ManyToManyField(Technology, blank=True, related_name="courses")
    level             = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    # language          = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="uz")
    price             = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_published      = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def total_duration_hours(self):
        total = sum(l.duration for m in self.modules.all() for l in m.lessons.all())
        return round(total / 60, 1)

    @property
    def total_lessons(self):
        return sum(m.lessons.count() for m in self.modules.all())

    @property
    def average_rating(self):
        qs = self.reviews.all()
        return round(sum(r.rating for r in qs) / qs.count(), 1) if qs.exists() else 0.0

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
    



class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title  = models.CharField(max_length=255)
    order  = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]


class Lesson(models.Model):
    module     = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title      = models.CharField(max_length=255)
    video      = models.FileField(upload_to='lessons/videos/', blank=True, null=True)  # ← MinIO
    duration   = models.PositiveIntegerField(default=0)
    order      = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]

class Enrollment(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → {self.course}"

    class Meta:
        unique_together = ("user", "course")


class LessonProgress(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progresses")
    lesson       = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progresses")
    is_completed = models.BooleanField(default=False)
    watched_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{'✓' if self.is_completed else '○'} {self.user} — {self.lesson}"

    class Meta:
        unique_together = ("user", "lesson")


class Review(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating     = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → {self.course} ({self.rating}★)"

    class Meta:
        unique_together = ("user", "course")