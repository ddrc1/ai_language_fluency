from time import time

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langgraph.graph.state import CompiledStateGraph

from apps.llm.model import ChatAI
from apps.llm.llm_models import get_llm_model
from apps.llm.prompt import PROMPT

fallback_models: ModelFallbackMiddleware = ModelFallbackMiddleware(
    get_llm_model(model_name="gemini-3.7-flash", temperature=0.7),
    get_llm_model(model_name="gemini-3.6-flash", temperature=0.7),
    get_llm_model(model_name="gemini-3.5-flash", temperature=0.7),
    get_llm_model(model_name="gemini-3.5-flash-lite", temperature=0.7)
)

_agent: CompiledStateGraph = create_agent(
    model=get_llm_model(temperature=0.7),
    middleware=[fallback_models],
)

def call_exercice_agent(user_message: str, message_history: list[ChatAI], language: str, qtd_examples: int, extra_words: list[str] | None = None) -> tuple[AIMessage, int]:
    if extra_words is None:
        extra_words = []
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

    prompt: list[BaseMessage] = template.format_prompt(messages=messages, language=language, qtd_examples=qtd_examples, extra_words=extra_words)
  
    start_time: float = time()
    response: dict = _agent.invoke(input=prompt)
    latency: int = int(time() - start_time)

    ai_message: AIMessage = response["messages"][-1]

    return ai_message, latency