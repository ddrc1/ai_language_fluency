from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from apps.llm.model import ChatAI
from apps.llm.serializers import ExerciseAgentSerializer, ChatHistorySerializer


class MessageView(views.APIView):
    serializer_class = ExerciseAgentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ExerciseAgentSerializer(), responses={status.HTTP_201_CREATED: ExerciseAgentSerializer()})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class MessageHistoryView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        histories = ChatAI.objects.filter(conversation_id__startswith=f"{request.user.username}_").order_by('-created_at')
        serializer = ChatHistorySerializer(histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)