from langchain_core.messages import AIMessage
from rest_framework import serializers
from uuid import uuid4

from apps.authentication.models import User
from apps.llm.model import ChatAI

from apps.llm.agent import call_exercice_agent


class ExerciseAgentSerializer(serializers.Serializer):
    conversation_id = serializers.CharField(required=False)
    message = serializers.CharField()
    language = serializers.CharField()

    def to_representation(self, instance: ChatAI):
        return {
            "conversation_id": instance.conversation_id,
            "user_message": instance.user_message,
            "ai_message": instance.ai_message,
            "llm_model": instance.llm_model,
            "input_tokens": instance.input_tokens,
            "output_tokens": instance.output_tokens,
            "latency": instance.latency
        }

    def validate(self, attrs):
        user: User = self.context["request"].user
        conversation_id: str = user.username + "_" + attrs.get("conversation_id", str(uuid4()))

        attrs["conversation_id"] = conversation_id

        return attrs
    
    def create(self, validated_data):
        message_history: list[ChatAI] = list(ChatAI.objects.filter(conversation_id=validated_data["conversation_id"]).order_by("created_at"))

        response: AIMessage
        latency: int
        response, latency = call_exercice_agent(user_message=validated_data["message"], message_history=message_history, language=validated_data["language"])
        response_metadata: dict = response.response_metadata if response.response_metadata else {}
        usage_metadata: dict = response.usage_metadata if response.usage_metadata else {}

        chat_ai: ChatAI = ChatAI.objects.create(
            conversation_id=validated_data["conversation_id"], 
            user_message=validated_data["message"], 
            ai_message=response.content, 
            llm_model=response_metadata.get("model_name", "unknown"), 
            input_tokens=usage_metadata.get("input_tokens", 0), 
            output_tokens=usage_metadata.get("output_tokens", 0),
            latency=latency
        )
        
        return chat_ai
