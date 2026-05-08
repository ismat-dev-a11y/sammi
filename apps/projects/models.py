# models.py
from django.db import models
from django.utils.text import slugify
from apps.courses.models import Technology


class Project(models.Model):
    DIFFICULTY_CHOICES = [
        ("beginner",     "Oson"),
        ("intermediate", "O'rta"),
        ("advanced",     "Murakkab"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to="projects/images/")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    github_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    technologies = models.ManyToManyField(Technology, blank=True, related_name="projects")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_steps(self):
        return self.steps.count()

    @total_steps.setter
    def total_steps(self, value):
        pass
    @property
    def total_duration_str(self):
        total = sum(s.duration for s in self.steps.all())
        h, m = divmod(total, 60)
        return f"{h} soat {m} daqiqa"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Handle duplicate slugs
            original_slug = self.slug
            counter = 1
            while Project.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProjectStep(models.Model):
    project   = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="steps")
    title     = models.CharField(max_length=255)
    # MinIO dagi fayl nomi (masalan: "projects/videos/telegram-clone/step-1.mp4")
    video_key = models.CharField(max_length=500, blank=True)
    # Frontendga beriladigan to'liq URL (MinIO public yoki presigned)
    video_url = models.URLField(blank=True)
    duration  = models.PositiveIntegerField(default=0)  # daqiqada
    order     = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.order}. {self.title}"

    class Meta:
        ordering = ["order"]


class ProjectFeature(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="features")
    text    = models.CharField(max_length=255)
    order   = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["order"]