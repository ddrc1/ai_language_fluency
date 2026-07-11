from django.urls import path
from apps.llm import views

urlpatterns = [
    path(r'send_message/', views.MessageView.as_view(), name='message'),
    path(r'history/', views.MessageHistoryView.as_view(), name='history'),
]
