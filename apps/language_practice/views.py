from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema

from apps.language_practice.models import Vocabulary, UserVocabulary
from apps.language_practice.serializers import VocabularySerializer, UserVocabularySerializer
from apps.language_practice.swagger.swagger_serializers import VocabularyResponseSerializer, UserVocabularyResponseSerializer, LanguageResponseSerializer


class DefaultViewSet(viewsets.ModelViewSet):
    http_method_names = ['post', 'get', 'delete', 'put']

    def get_queryset(self):
        return self.queryset.order_by('pk')
    
    def perform_destroy(self, instance):
        instance.enable = False
        instance.save()


class LanguageViewSet(DefaultViewSet):
    queryset = Vocabulary.objects.filter(enable=True)
    serializer_class = VocabularySerializer

    @swagger_auto_schema(responses={status.HTTP_200_OK: LanguageResponseSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_200_OK: LanguageResponseSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_201_CREATED: LanguageResponseSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_200_OK: LanguageResponseSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class VocabularyViewSet(DefaultViewSet):
    queryset = Vocabulary.objects.filter(enable=True)
    serializer_class = VocabularySerializer

    @swagger_auto_schema(responses={status.HTTP_200_OK: VocabularyResponseSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_200_OK: VocabularyResponseSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_201_CREATED: VocabularyResponseSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_200_OK: VocabularyResponseSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    

class UserVocabularyViewSet(DefaultViewSet):
    queryset = UserVocabulary.objects.filter(enable=True)
    serializer_class = UserVocabularySerializer

    @swagger_auto_schema(responses={status.HTTP_200_OK: VocabularyResponseSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_200_OK: UserVocabularyResponseSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_201_CREATED: UserVocabularyResponseSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_200_OK: UserVocabularyResponseSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)