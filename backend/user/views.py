"""Views for user api"""

from django.contrib.auth import authenticate
from django.utils.timezone import now
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from user.serializer import (
    UserSerializer,
    SendEmailSerializer,
    ForgotPasswordUserChangeSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer


class LoginUserView(APIView):
    """
    Login user and return JWT tokens
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(email=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class UpdateUserView(generics.RetrieveUpdateAPIView):
    """Retrive  and update the user"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ForgotPasswordUserView(APIView):
    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {
                    "message": "An email will be sent to you within 1 min to reset your password"
                },
                status=status.HTTP_200_OK,
            )


class ForgotPasswordUserChangeView(APIView):
    def patch(self, request, uid, token, format=None):
        serializer = ForgotPasswordUserChangeSerializer(
            data=request.data, context={"uid": uid, "token": token}
        )
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "password changed sucessfully"})
        else:
            return Response({"error": "some error happend"})


class UpdateLastVisitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user.last_visit = now()
        user.save(update_fields=["last_visit"])
        return Response({"status": "last_visit updated"})
