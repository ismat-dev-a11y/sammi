from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema, OpenApiTypes
from drf_spectacular.openapi import AutoSchema
from .serializers import ProfileSerializer, ChangePasswordSerializer

@extend_schema(tags=['Profile'])
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'full_name': {'type': 'string'},
                    'nickname': {'type': 'string'},
                    'bio': {'type': 'string'},
                    'email': {'type': 'string'},
                    'avatar_url': {'type': 'string', 'format': 'binary'},  # ← shu muhim
                    'language_code': {'type': 'string'},
                    'country': {'type': 'string'},
                }
            }
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'full_name': {'type': 'string'},
                    'nickname': {'type': 'string'},
                    'bio': {'type': 'string'},
                    'email': {'type': 'string'},
                    'avatar_url': {'type': 'string', 'format': 'binary'},  # ← shu muhim
                    'language_code': {'type': 'string'},
                    'country': {'type': 'string'},
                }
            }
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

@extend_schema(tags=['Profile'], request=ChangePasswordSerializer)
class ChangePasswordView(APIView):
    """
    POST /api/settings/change-password/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)