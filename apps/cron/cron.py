import os
import random
from uuid import uuid4
from dotenv import load_dotenv

from django.core.mail import send_mail
from django.db.models.manager import BaseManager

from langchain_core.messages import AIMessage

from apps.authentication.models import User
from apps.language_practice.models import UserVocabulary
from apps.llm.model import ChatAI
from apps.llm.agent import call_exercice_agent

load_dotenv()

WORDS_TO_SEND: int = int(os.getenv("WORDS_TO_SEND", 5))
EMAIL_HOST_USER: str = os.getenv("FROM_EMAIL", "")


def send_practice_email(user_email: str, email_content: str):
    subject: str = "Your Daily Language Practice"
    message: str = email_content
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email to {user_email}: {e}")

def generate_email_content():
    users: BaseManager[User] = User.objects.filter(is_active=True, keep_sending_taks=True)
    
    response: AIMessage
    latency: int

    for user in users:
        user_vocabulary: BaseManager[UserVocabulary] = UserVocabulary.objects.filter(user=user, enable=True)
        distinct_languages: list[dict] = user_vocabulary.values('vocabulary__language').distinct()

        for language in distinct_languages:
            user_vocabulary_language = user_vocabulary.filter(vocabulary__language=language['vocabulary__language'])

            
            if user_vocabulary_language.exists():
                ready_for_practice: list[str] = [uv.vocabulary.word_vocab for uv in user_vocabulary if uv.ready_for_practice]
                chosen_words: list[str] = random.choices(ready_for_practice, k=min(WORDS_TO_SEND, len(ready_for_practice)))

                response, latency = call_exercice_agent(user_message=" ".join(chosen_words), message_history=[], language=language['vocabulary__language'])
                response_metadata: dict = response.response_metadata if response.response_metadata else {}
                usage_metadata: dict = response.usage_metadata if response.usage_metadata else {}
                
                ChatAI.objects.create(
                    conversation_id=user.username + "_" + str(uuid4()), 
                    user_message=" ".join(chosen_words),
                    ai_message=response.content, 
                    llm_model=response_metadata.get("model_name", "unknown"), 
                    input_tokens=usage_metadata.get("input_tokens", 0), 
                    output_tokens=usage_metadata.get("output_tokens", 0),
                    latency=latency
                )
                
                send_practice_email(user_email=user.email, email_content=response.content)
