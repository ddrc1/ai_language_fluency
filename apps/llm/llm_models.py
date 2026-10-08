import os

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gemini-3.5-flash")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "CHAVE_DO_GEMINI")

def get_llm_model(model_name: str = DEFAULT_LLM_MODEL, temperature: float = 0) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name, 
        temperature=temperature, 
        thinking_budget=-1, 
        thinking_level="high",
        api_key=GEMINI_API_KEY,
        retries=3
    )
