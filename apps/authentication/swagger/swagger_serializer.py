from rest_framework import serializers

from apps.authentication.serializers import TokensSerializer
from apps.authentication.models import User

class SwaggerLoginSerializer(serializers.ModelSerializer):
    tokens = TokensSerializer()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'tokens']