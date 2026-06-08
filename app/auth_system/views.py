from django.shortcuts import render

import bcrypt
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_system.models import Session
from auth_system.serializers import RegisterSerializer, LoginSerializer
from auth_system.services import create_access_token
from users.models import User
from django.conf import settings


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user = serializer.save()

        return Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": user.middle_name,
                "message": "User registered successfully",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response(
                {"detail": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        if not user.is_active:
            return Response(
                {"detail": "User account is inactive"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        password_is_valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8"),
        )

        if not password_is_valid:
            return Response(
                {"detail": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        expires_at = timezone.now() + settings.JWT_ACCESS_TOKEN_LIFETIME

        session = Session.objects.create(
            user=user,
            expires_at=expires_at,
        )

        access_token = create_access_token(
            user_id=user.id,
            session_id=session.id,
            token_jti=session.token_jti,
        )

        return Response(
            {
                "access_token": access_token,
                "token_type": "Bearer"
            },
            status=status.HTTP_200_OK,
        )


class AuthMeView(APIView):
    def get(self, request):
        if not request.user or not getattr(request.user, "is_active", False):
            return Response(
                {"detail": "Authentification credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
                {
                    "id": request.user.id,
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "middle_name": request.user.middle_name,
                },
                status=status.HTTP_200_OK
            )


class LogoutView(APIView):
    def post(self, request):
        if request.auth_session is None:
            return Response(
                {"detail": "Authentication credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        request.auth_session.is_active = False
        request.auth_session.revoked_at = timezone.now()
        request.auth_session.save(
            update_fields=["is_active", "revoked_at"]
        )

        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )