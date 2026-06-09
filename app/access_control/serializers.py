from rest_framework import serializers

from access_control.models import AccessRoleRule, BusinessElement, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "code",
            "description"
        ]


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = [
            "id",
            "name",
            "code",
            "description"
        ]
    

class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role_code = serializers.CharField(source="role.code", read_only=True)
    element_code = serializers.CharField(source="element.code", read_only=True)

    class Meta:
        model = AccessRoleRule
        fields = [
            "id",
            "role",
            "role_code",
            "element",
            "element_code",
            "read_permission",
            "read_all_permission",
            "create_permission",
            "update_permission",
            "update_all_permission",
            "delete_permission",
            "delete_all_permission",
        ]