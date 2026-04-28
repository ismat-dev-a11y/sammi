from django.core.serializers import serialize
from django.forms import EmailField
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
User = get_user_model()

from .serializers import GoogleAuthSerializer, UserSerializer, UserUpdateSerializer, SendEmailOTPSerializer, VerifyEmailOTPSerializer


def _jwt_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }

extend_schema(summary='Google auth')
class GoogleAuthView(GenericAPIView):
    permission_classes     = [AllowAny]
    authentication_classes = []
    serializer_class       = GoogleAuthSerializer

    @extend_schema(
        request=GoogleAuthSerializer,
        # security=[],
        responses={
            200: UserSerializer,
            201: UserSerializer,
            400: OpenApiResponse(description="Token yaroqsiz"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user, created = serializer.get_or_create_user()

        return Response(
            {
                "user":    UserSerializer(user).data,
                "tokens":  _jwt_tokens(user),
                "created": created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MeView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = UserSerializer

    def get(self, request):
        return Response(self.get_serializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

@extend_schema(summary='OTP yuborish', tags=['Accounts'])
class SendEmailOTPView(GenericAPIView):
    serializer_class = SendEmailOTPSerializer  # ✅ shu yoq qolgan edi

    def post(self, request):
        serializer = self.get_serializer(data=request.data)  # ✅ self.get_serializer

        if serializer.is_valid():
            return Response(
                {"message": "OTP emailga yuborildi"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(summary='OTP tasdiqlash', tags=['Accounts'])
class VerifyEmailOTPView(GenericAPIView):
    serializer_class = VerifyEmailOTPSerializer  # ✅ shu ham

    def post(self, request):
        serializer = self.get_serializer(data=request.data)  # ✅ self.get_serializer

        if serializer.is_valid():
            email = serializer.validated_data['email']
            user, created = User.objects.get_or_create(email=email)

            if created or user.is_new_user:
                user.is_new_user = False
                user.save(update_fields=['is_new_user'])

            tokens = _jwt_tokens(user)

            return Response(
                {
                    "message": "OTP tasdiqlandi",
                    "refresh": tokens['refresh'],
                    "access": tokens['access'],
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)