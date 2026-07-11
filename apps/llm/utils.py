from uuid import uuid4
from datetime import datetime
from django.core.mail import send_mail
from langchain.messages import AIMessage
from dotenv import load_dotenv
import os

from apps.llm.agent import call_exercice_agent
from apps.llm.model import ChatAI
from apps.language_practice.models import Language
from apps.authentication.models import User

load_dotenv()

EMAIL_HOST_USER: str = os.getenv("FROM_EMAIL", "")
QTD_EXAMPLES: int = os.getenv("QTD_EXAMPLES", 5)

def practice(words: list[str], language: Language, user: User, send_email=True):
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

    try:
        response: AIMessage
        latency: int
        response, latency = call_exercice_agent(user_message="; ".join(words), message_history=[], language=language.name, qtd_examples=QTD_EXAMPLES)
        response_metadata: dict = response.response_metadata if response.response_metadata else {}
        usage_metadata: dict = response.usage_metadata if response.usage_metadata else {}

        response = response.content
        if type(response) == list and len(response) > 0 and response[0].get("type") == "text":
            response = response[0].get("text")
        
        ChatAI.objects.create(
            conversation_id=user.username + "_" + str(uuid4()), 
            user_message=", ".join(words),
            ai_message=response, 
            llm_model=response_metadata.get("model_name", "unknown"), 
            input_tokens=usage_metadata.get("input_tokens", 0), 
            output_tokens=usage_metadata.get("output_tokens", 0),
            latency=latency
        )

        if send_email:
            send_practice_email(user_email=user.email, email_content=response)

    except Exception as e:
        print(e)