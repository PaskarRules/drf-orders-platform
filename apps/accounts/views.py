import logging

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger("apps.accounts")

from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
    LogoutSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user and return JWT tokens."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": ProfileSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's profile."""

    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change the authenticated user's password."""

    permission_classes = (IsAuthenticated,)

    def post(self, request) -> Response:
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password updated."}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Blacklist the refresh token to log out."""

    permission_classes = (IsAuthenticated,)

    def post(self, request) -> Response:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            logger.warning("Logout failed: invalid or expired refresh token")
        return Response(status=status.HTTP_205_RESET_CONTENT)
