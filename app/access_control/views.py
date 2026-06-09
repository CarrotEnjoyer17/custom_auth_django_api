from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from access_control.models import AccessRoleRule, BusinessElement, Role
from access_control.serializers import (
    AccessRoleRuleSerializer,
    RoleSerializer,
    BusinessElementSerializer,
)
from access_control.services import has_permission


def get_authenticated_user(request):
    user = getattr(request, "jwt_user", None)

    if not user or not getattr(user, "is_active", False):
        return None

    return user


class RoleListView(APIView):
    def get(self, request):
        user = get_authenticated_user(request)

        if user is None:
            return Response(
                {"detail": "Authentification credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        if not has_permission(user, "access_rules", "read"):
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

class AccessRoleRuleListView(APIView):
    def get(self, request):
        user = get_authenticated_user(request)

        if user is None:
            return Response(
                {"detail": "Authentication credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not has_permission(user, "access_rules", "read"):
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        rules = AccessRoleRule.objects.select_related("role", "element").all()
        serializer = AccessRoleRuleSerializer(rules, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class BusinessElementListView(APIView):
    def get(self, request):
        user = get_authenticated_user(request)

        if user is None:
            return Response(
                {"detail": "Authentication credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not has_permission(user, "access_rules", "read"):
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )

        elements = BusinessElement.objects.all()
        serializer = BusinessElementSerializer(elements, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )



class AccessRoleRuleDetailView(APIView):
    def patch(self, request, rule_id):
        user = get_authenticated_user(request)

        if user is None:
            return Response(
                {"detail": "Authentication credentials were not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not has_permission(user, "access_rules", "update"):
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )

        rule = AccessRoleRule.objects.filter(id=rule_id).first()

        if rule is None:
            return Response(
                {"detail": "Access rule not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = AccessRoleRuleSerializer(
            rule,
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
