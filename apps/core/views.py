from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .serializers import ProfileSerializer, ChangePasswordSerializer

@extend_schema(tags=['Profile'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/settings/profile/  → profilni yuklash
    PATCH /api/settings/profile/  → Save Profile tugmasi
    """
    serializer_class   = ProfileSerializer
    permission_classes = [IsAuthenticated]

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