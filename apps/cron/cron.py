import os
import random
from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv

from django.core.mail import send_mail
from django.db.models.manager import BaseManager

from langchain_core.messages import AIMessage

from apps.authentication.models import User
from apps.language_practice.models import UserVocabulary, Language, Vocabulary
from apps.llm.model import ChatAI
from apps.llm.agent import call_exercice_agent

load_dotenv()

WORDS_TO_SEND: int = int(os.getenv("WORDS_TO_SEND", 5))
EMAIL_HOST_USER: str = os.getenv("FROM_EMAIL", "")


def send_practice_email(user_email: str, email_content: str):
    today_date = datetime.now().strftime('%d/%m/%Y') 
    subject: str = f"Your Daily Language Practice ({today_date})"
    
    try:
        send_mail(
            subject=subject,
            message=email_content,
            from_email=EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email to {user_email}: {e}")

def generate_email_content():
    try:
        users: BaseManager[User] = User.objects.filter(is_active=True, keep_sending_taks=True)
        languages: BaseManager[Language] = Language.objects.filter(enable=True)
        
        response: AIMessage
        latency: int

        for user in users:
            user_vocabulary: BaseManager[UserVocabulary] = UserVocabulary.objects.filter(user=user, enable=True)

            for language in languages:
                user_vocabulary_language = user_vocabulary.filter(vocabulary__language=language)

                if user_vocabulary_language.exists():
                    vocab_for_practice: list[UserVocabulary] = [uv for uv in user_vocabulary if uv.ready_for_practice]
                    chosen_vocab: list[UserVocabulary] = random.choices(vocab_for_practice, k=min(WORDS_TO_SEND, len(vocab_for_practice)))
                    words: list[str] = [vocab.vocabulary.word_vocab for vocab in chosen_vocab]

                    response, latency = call_exercice_agent(user_message=", ".join(words), message_history=[], language=language.name)
                    response_metadata: dict = response.response_metadata if response.response_metadata else {}
                    usage_metadata: dict = response.usage_metadata if response.usage_metadata else {}
                    
                    ChatAI.objects.create(
                        conversation_id=user.username + "_" + str(uuid4()), 
                        user_message=", ".join(words),
                        ai_message=response.content, 
                        llm_model=response_metadata.get("model_name", "unknown"), 
                        input_tokens=usage_metadata.get("input_tokens", 0), 
                        output_tokens=usage_metadata.get("output_tokens", 0),
                        latency=latency
                    )
                    
                    send_practice_email(user_email=user.email, email_content=response.content)

                    for user_vocab in chosen_vocab:
                        user_vocab.practice_count += 1
                        user_vocab.last_practiced = datetime.now()
                    
                    UserVocabulary.objects.bulk_update(objs=chosen_vocab, fields=["practice_count", "last_practiced"])
    except Exception as e:
        print(e)
