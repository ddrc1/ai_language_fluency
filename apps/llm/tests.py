from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.llm.model import ChatAI
from apps.llm.serializers import ExerciseAgentSerializer


User = get_user_model()


class ChatAIModelTests(TestCase):
    def test_string_representation_uses_ai_message(self):
        chat = ChatAI.objects.create(
            conversation_id='user_123',
            user_message='Hello',
            ai_message='Hi there! This is a long message to check the truncation.',
            llm_model='gemini-3.5-flash',
            input_tokens=10,
            output_tokens=8,
            latency=1.7,
        )

        expected = f"{chat.conversation_id} - {chat.ai_message[:50]}"
        self.assertEqual(str(chat), expected)


class ExerciseAgentSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='securepass123',
        )

    @patch('apps.llm.serializers.call_exercice_agent')
    def test_create_persists_ai_response(self, mock_agent):
        mock_agent.return_value = (
            SimpleNamespace(
                content='Bonjour !',
                response_metadata={'model_name': 'gemini-3.5-flash'},
                usage_metadata={'input_tokens': 12, 'output_tokens': 7},
            ),
            2,
        )

        serializer = ExerciseAgentSerializer(
            data={'message': 'bonjour', 'language': 'French'},
            context={'request': SimpleNamespace(user=self.user)},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        chat = serializer.save()

        self.assertTrue(chat.conversation_id.startswith(f'{self.user.username}_'))
        self.assertEqual(chat.user_message, 'bonjour')
        self.assertEqual(chat.ai_message, 'Bonjour !')
        self.assertEqual(chat.llm_model, 'gemini-3.5-flash')
        self.assertEqual(chat.input_tokens, 12)
        self.assertEqual(chat.output_tokens, 7)
        self.assertEqual(chat.latency, 2)
        mock_agent.assert_called_once_with(
            user_message='bonjour',
            message_history=[],
            language='French',
            qtd_examples=3,
            extra_words=[],
        )


class MessageViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='securepass123',
        )
        self.client = APIClient()

    @patch('apps.llm.serializers.call_exercice_agent')
    def test_post_creates_chat_message(self, mock_agent):
        mock_agent.return_value = (
            SimpleNamespace(
                content='Hola!',
                response_metadata={'model_name': 'gemini-3.5-flash'},
                usage_metadata={'input_tokens': 9, 'output_tokens': 4},
            ),
            4,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('message:message'),
            {'message': 'hello', 'language': 'Spanish'},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ChatAI.objects.count(), 1)
        self.assertEqual(response.data['user_message'], 'hello')
        self.assertEqual(response.data['ai_message'], 'Hola!')
        self.assertEqual(response.data['llm_model'], 'gemini-3.5-flash')


class MessageHistoryViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='carol',
            email='carol@example.com',
            password='securepass123',
        )
        self.other_user = User.objects.create_user(
            username='daniel',
            email='daniel@example.com',
            password='securepass123',
        )
        self.client = APIClient()

    def test_get_returns_only_current_user_history(self):
        ChatAI.objects.create(
            conversation_id='carol_aaa',
            user_message='first',
            ai_message='first reply',
            llm_model='gemini-3.5-flash',
            input_tokens=1,
            output_tokens=1,
            latency=1.0,
        )
        ChatAI.objects.create(
            conversation_id='carol_bbb',
            user_message='second',
            ai_message='second reply',
            llm_model='gemini-3.5-flash',
            input_tokens=1,
            output_tokens=1,
            latency=1.0,
        )
        ChatAI.objects.create(
            conversation_id='daniel_zzz',
            user_message='foreign',
            ai_message='hidden reply',
            llm_model='gemini-3.5-flash',
            input_tokens=1,
            output_tokens=1,
            latency=1.0,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('message:history'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(all(item['conversation_id'].startswith('carol_') for item in response.data))
