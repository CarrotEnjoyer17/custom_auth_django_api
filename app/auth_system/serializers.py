import bcrypt
from rest_framework import serializers

from access_control.models import Role, UserRole
from users.models import User

class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    middle_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    email = serializers.EmailField()

    password = serializers.CharField(write_only=True, min_length=8)
    password_repeat = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def validate(self, attrs):
        if attrs["password"] != attrs["password_repeat"]:
            raise serializers.ValidationError(
                {"password_repeat": "Passwords do not match"}
            )
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_repeat")

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        user = User.objects.create(
            **validated_data,
            password_hash=password_hash,
        )

        default_role = Role.objects.filter(code="user").first()

        if default_role is None:
            User.objects.create(
                user=user,
                role=default_role,
            )
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

