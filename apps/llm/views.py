from rest_framework import views, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from apps.llm.serializers import ExerciseAgentSerializer


class MessageView(views.APIView):
    serializer_class = ExerciseAgentSerializer

    @swagger_auto_schema(request_body=ExerciseAgentSerializer(), responses={status.HTTP_201_CREATED: ExerciseAgentSerializer()})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)