from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import GoogleAuthSerializer, UserRegistrationSerializer, UserLoginSerializer, UserSerializer, UserUpdateSerializer


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


@extend_schema(summary='User registration', tags=['Accounts'])
class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(description="User successfully registered"),
            400: OpenApiResponse(description="Validation errors"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": _jwt_tokens(user),
                "message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi"
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(summary='User registration', tags=['Accounts'])
class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserLoginSerializer

    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful"),
            401: OpenApiResponse(description="Invalid credentials"),
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        
        # Reset is_new_user flag if it was True
        if user.is_new_user:
            user.is_new_user = False
            user.save(update_fields=['is_new_user'])
        
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": _jwt_tokens(user),
                "message": "Tizimga muvaffaqiyatli kirdingiz"
            },
            status=status.HTTP_200_OK
        )