from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsStaff, IsSelfOrStaff
from users.serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, PasswordChangeSerializer

User = get_user_model()

class UserList(APIView):
    """
    Endpoints for both fetching all users and creating a new user.
    """
    allowed_methods = ['GET', 'POST']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsStaff()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="active",
                type=OpenApiTypes.BOOL,
                required=False,
                description="Filter users by their active status (true/false)"
            ),
        ]
    )
    def get(self, request):
        """
        Get a list of users
        """
        active = request.query_params.get('active', None)
        if active is not None:
            active = active.lower() in ['true', '1', 'yes']
            users = User.objects.filter(is_active=active)
        else:
            users = User.objects.all()

        serializer = self.get_serializer_class()(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new user.
        """
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    """
    Retrieve, update, or delete a user instance.
    """

    allowed_methods = ['GET', 'PUT', 'PATCH', 'DELETE']

    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [IsAuthenticated(), IsSelfOrStaff()]
        return [IsAuthenticated(), IsStaff()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        elif self.request.method == 'PUT':
            return UserUpdateSerializer
        return None

    def get_object(self, pk):
        obj = get_object_or_404(User, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, pk):
        """
        Get user data
        """
        user = self.get_object(pk)
        serializer = self.get_serializer_class()(user)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update a user
        """
        user = self.get_object(pk)
        serializer = self.get_serializer_class()(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Activate or deactivate a user
        """
        user = self.get_object(pk)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return Response(
            {"detail": f"User account has been {'activated' if user.is_active else 'deactivated'}"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        """
        Delete a user
        """
        user = self.get_object(pk)
        user.delete()
        return Response({"detail": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class ChangePassword(APIView):
    """
    Endpoint for changing current user's password
    """
    allowed_methods = ['POST']
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        """
        Change user password
        """
        user = request.user
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({"detail": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({"detail": "Password updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
