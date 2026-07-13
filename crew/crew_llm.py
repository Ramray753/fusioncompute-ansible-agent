import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables
load_dotenv()

def bootstrap_runtime_llm(model_env_key: str, url_env_key: str) -> LLM:
    """
    Parses configuration strings from the environment matrix and constructs
    a unified native crewai.LLM instance.
    """
    raw_model = os.getenv(model_env_key)
    target_url = os.getenv(url_env_key)
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not raw_model:
        raise ValueError(f"[FATAL ERROR] Requisite environmental variable '{model_env_key}' is undefined.")
    if not target_url:
        raise ValueError(f"[FATAL ERROR] Requisite environmental variable '{url_env_key}' is undefined.")
    if not api_key:
        raise ValueError("[SECURITY ALERT] Online provider requires 'OPENAI_API_KEY' to be populated.")
    
    cleaned_model = raw_model.split("/")[-1] if "/" in raw_model else raw_model
    
    return LLM(
        model=cleaned_model, 
        base_url=target_url, 
        api_key=api_key,
        temperature=0.1
    )

# Unified LLM instance replacing the previously separated analyst and coding LLMs
agent_llm = bootstrap_runtime_llm("AGENT_MODEL", "AGENT_BASE_URL")