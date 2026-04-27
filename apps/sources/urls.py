# apps/sources/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SourceCodeViewSet

router = DefaultRouter()
router.register(r"source-codes", SourceCodeViewSet, basename="source-code")

app_name = "sources"

urlpatterns = [
    path("", include(router.urls)),
]