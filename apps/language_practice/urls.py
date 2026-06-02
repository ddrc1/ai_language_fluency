from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.language_practice import views

router = DefaultRouter()

router.register(r'vocabulary', views.VocabularyViewSet, basename='vocabulary')
router.register(r'user_vocabulary', views.UserVocabularyViewSet, basename='user_vocabulary')

urlpatterns = router.urls