from rest_framework_simplejwt.views import TokenObtainPairView

from api.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Get JWT access and refresh tokens for authentication and authorization
    """
    serializer_class = CustomTokenObtainPairSerializer
