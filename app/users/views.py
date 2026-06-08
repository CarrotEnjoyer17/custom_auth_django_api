from django.shortcuts import render

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserProfileSerializer


class UserMeView(APIView):
    def get(self, request):
        user = getattr(request, "jwt_user", None)
        if not user or not getattr(user, "is_active", False):
            return Response(
                {"detail": "Authentification credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = UserProfileSerializer(user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        user = getattr(request, "jwt_user", None)
        if not user or not getattr(user, "is_active", False):
            return Response(
                {"detail": "Authentification credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = UserProfileSerializer(
            user,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    
    def delete(self, request):
        user = getattr(request, "jwt_user", None)
        if not user or not getattr(user, "is_active", False):
            return Response(
                {"detail": "Autentification credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.is_active = False
        user.deleted_at = timezone.now()
        user.save(update_fields=["is_active", "deleted_at", "updated_at"])

        if request.auth_session is not None:
            request.auth_session.is_active = False
            request.auth_session.revoked_at = timezone.now()
            request.auth_session.save(update_fields=["is_active", "revoked_at"])
        
        return Response(
            {"message": "User account successfully deleted"},
            status=status.HTTP_200_OK,
        )