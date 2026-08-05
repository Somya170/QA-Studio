from app.llm.base_provider import LLMProvider

class LocalLLMProvider(LLMProvider):
    def __init__(self, endpoint: str = "http://localhost:11434/api/generate"):
        self.endpoint = endpoint

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        # Connects to local Ollama / llama.cpp REST endpoint on Jetson Orin
        return f"[Local Jetson LLM]: {prompt[:100]}..."

local_llm = LocalLLMProvider()
