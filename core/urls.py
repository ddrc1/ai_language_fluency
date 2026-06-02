from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

router: DefaultRouter = DefaultRouter()

# Swagger schema view
schema_view = get_schema_view(
   openapi.Info(
      title="Language Fluency API",
      default_version='v1',
      description="API de aprendizagem de idiomas",
      terms_of_service=None,
      contact=openapi.Contact(email="danielrotheia@gmail.com"),
      license=None,
   ),
   permission_classes=(AllowAny,),
   public=True,
)

urlpatterns: list = [
    path('admin/', admin.site.urls),
    path(r'api/', include((router.urls, 'api'), namespace='api')),
    path(r'api/authentication/', include(('apps.authentication.urls', 'apps.authentication'), namespace='authentication')),
    path(r'api/language_practice/', include(('apps.language_practice.urls', 'apps.language_practice'), namespace="language_practice")),
    path(r'api/message/', include(('apps.llm.urls', 'apps.llm'), namespace="message")),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs')
]
