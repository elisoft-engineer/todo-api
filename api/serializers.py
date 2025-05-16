from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class EnumField(serializers.Field):
    def __init__(self, enum_class, *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if isinstance(value, self.enum_class):
            return value.value
        return str(value)

    def to_internal_value(self, data):
        try:
            return self.enum_class(data)
        except ValueError:
            raise serializers.ValidationError(detail=f"Invalid value for enum {self.enum_class.__name__}: {data}")

    def get_schema(self):
        return {
            "type": "string",
            "enum": [e.value for e in self.enum_class],
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(detail="Phone number and password are required.")

        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(detail="Invalid email number or password.")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
        }