from time import time

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain.agents import create_agent

from apps.llm.model import ChatAI
from apps.llm.llm_models import get_llm_model
from apps.llm.prompt import PROMPT

_llm_model = create_agent(
    model=get_llm_model(temperature=0.7)
)

def call_exercice_agent(user_message: str, message_history: list[ChatAI], language: str, qtd_examples: int) -> tuple[AIMessage, int]:
    if message_history:
        messages: list[BaseMessage] = []
        for message in message_history:
            messages.append(HumanMessage(content=message.user_message))
            messages.append(AIMessage(content=message.ai_message))
    else:
        messages = []
    
    template = ChatPromptTemplate([
        SystemMessagePromptTemplate.from_template(template=PROMPT),
        MessagesPlaceholder(variable_name="messages"),
        HumanMessage(content=user_message)
    ])

    prompt: list[BaseMessage] = template.format_prompt(messages=messages, language=language, qtd_examples=qtd_examples)
  
    start_time: float = time()
    response: dict = _llm_model.invoke(input=prompt)
    latency: int = int(time() - start_time)

    ai_message: AIMessage = response["messages"][-1]

    return ai_message, latency