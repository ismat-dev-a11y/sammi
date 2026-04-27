# apps/sources/models.py
from django.db import models
from django.utils.text import slugify
from apps.courses.models import Technology


class SourceCode(models.Model):
    title        = models.CharField(max_length=255)
    slug         = models.SlugField(unique=True, blank=True)
    github_url   = models.URLField()
    technologies = models.ManyToManyField(Technology, blank=True, related_name="source_codes")
    order        = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            counter = 1
            while SourceCode.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Source Code"
        verbose_name_plural = "Source Codes"