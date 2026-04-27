# apps/sources/views.py
from rest_framework import viewsets
from .models import SourceCode
from .serializers import (
    SourceCodeListSerializer,
    SourceCodeDetailSerializer,
    SourceCodeCreateUpdateSerializer,
)


class SourceCodeViewSet(viewsets.ModelViewSet):
    queryset = SourceCode.objects.filter(is_published=True).prefetch_related("technologies")
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return SourceCodeListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return SourceCodeCreateUpdateSerializer
        return SourceCodeDetailSerializer