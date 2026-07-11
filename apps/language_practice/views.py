from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from apps.llm.utils import practice

from apps.language_practice.models import Language, Vocabulary, UserVocabulary
from apps.language_practice.serializers import LanguageSerializer, VocabularySerializer, UserVocabularySerializer
from apps.language_practice.swagger.swagger_serializers import VocabularyResponseSerializer, UserVocabularyResponseSerializer, LanguageResponseSerializer


class DefaultViewSet(viewsets.ModelViewSet):
    http_method_names = ['post', 'get', 'delete', 'put']

    def get_queryset(self):
        return self.queryset.order_by('pk')

    def perform_destroy(self, instance):
        instance.enable = False
        instance.save()


class LanguageViewSet(DefaultViewSet):
    queryset = Language.objects.filter(enable=True)
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={status.HTTP_200_OK: LanguageResponseSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: LanguageResponseSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_201_CREATED: LanguageResponseSerializer()})
    def create(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: LanguageResponseSerializer()})
    def update(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        return super().update(request, *args, **kwargs)


class VocabularyViewSet(DefaultViewSet):
    queryset = Vocabulary.objects.filter(enable=True)
    serializer_class = VocabularySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={status.HTTP_200_OK: VocabularyResponseSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: VocabularyResponseSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_201_CREATED: VocabularyResponseSerializer()})
    def create(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: VocabularyResponseSerializer()})
    def update(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        return super().update(request, *args, **kwargs)


class UserVocabularyViewSet(DefaultViewSet):
    queryset = UserVocabulary.objects.filter(enable=True)
    serializer_class = UserVocabularySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()        
        return qs.filter(user=self.request.user)

    @swagger_auto_schema(responses={status.HTTP_200_OK: UserVocabularyResponseSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_201_CREATED: UserVocabularyResponseSerializer()})
    def create(self, request, *args, **kwargs):
        print("OK")
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='mark-practiced')
    def mark_practiced(self, request, *args, **kwargs):
        instance: UserVocabulary = self.get_object()

        try:
            practice(words=[instance.vocabulary.word_vocab], language=instance.vocabulary.language, user=request.user, send_email=False)
            instance.mark_as_practiced()
        except:
            Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)