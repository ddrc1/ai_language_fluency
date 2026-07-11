"""
Views for the login module.
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import login, logout
from apps.cron.cron import generate_email_content

from apps.authentication.models import User
from apps.authentication.serializers import RegisterSerializer, LoginSerializer, LogoutSerializer
from apps.authentication.swagger.swagger_serializer import SwaggerLoginSerializer


class RegisterView(views.APIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer(), responses={status.HTTP_201_CREATED: None})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_201_CREATED)
    

class LoginView(views.APIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer(), 
                         responses={status.HTTP_200_OK: SwaggerLoginSerializer()})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        login(request, serializer.validated_data)
        generate_email_content()
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    serializer_class = LogoutSerializer

    @swagger_auto_schema(request_body=LogoutSerializer())
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            logout(request)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
