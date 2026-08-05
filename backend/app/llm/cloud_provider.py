import google.generativeai as genai
import requests
import time
import os
from app.config import GEMINI_API_KEY, GROQ_API_KEY
from app.llm.base_provider import LLMProvider

class CloudLLMProvider(LLMProvider):
    def __init__(self):
        self.gemini_key = GEMINI_API_KEY
        self.groq_key = GROQ_API_KEY
        self.gemini_initialized = False
        self._init_gemini()

    def _init_gemini(self):
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.gemini_initialized = True
            except Exception as e:
                print("Gemini Initialization Error:", e)

    @property
    def initialized(self) -> bool:
        """Returns True if either Groq or Gemini is configured."""
        self._reload_keys()
        return bool(self.groq_key or self.gemini_initialized)

    def _reload_keys(self):
        # Hot-reload keys in case .env was updated at runtime
        from app.config import GEMINI_API_KEY, GROQ_API_KEY
        self.gemini_key = GEMINI_API_KEY
        self.groq_key = GROQ_API_KEY
        if self.gemini_key and not self.gemini_initialized:
            self._init_gemini()

    def _generate_groq(self, prompt: str, system_prompt: str = "") -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.1
        }
        
        max_retries = 3
        delay = 2.0
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        print(f"Groq Rate Limit (429) hit. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= 2
                        continue
                    return f"API Query Error: Groq rate limit exceeded (429)."
                else:
                    return f"API Query Error: Groq returned {response.status_code} - {response.text}"
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                return f"API Query Error: Groq request failed - {str(e)}"
        
        return "API Query Error: Groq request timeout/exhausted."

    def _generate_gemini(self, prompt: str, system_prompt: str = "") -> str:
        max_retries = 3
        delay = 2.0
        
        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-3.5-flash",
                    system_instruction=system_prompt if system_prompt else None
                )
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        print(f"Gemini Rate Limit (429) hit. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= 2
                        continue
                return f"API Query Error: {error_str}"
        
        return "API Query Error: Gemini request timeout."

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        self._reload_keys()

        # Prioritize Groq if API key is present
        if self.groq_key:
            return self._generate_groq(prompt, system_prompt=system_prompt)
            
        # Fall back to Gemini if API key is present
        elif self.gemini_initialized:
            return self._generate_gemini(prompt, system_prompt=system_prompt)
            
        # Error / Configuration prompt if neither key exists
        else:
            return (
                "⚠️ LLM provider is not configured.\n\n"
                "Please add either `GROQ_API_KEY` or `GEMINI_API_KEY` in the `backend/.env` file:\n"
                "```env\n"
                "GROQ_API_KEY=your_groq_key_here\n"
                "# OR\n"
                "GEMINI_API_KEY=your_gemini_key_here\n"
                "```\n"
                "Once added, restart the server or refresh to activate dynamic AI queries!"
            )

# Singleton provider instance
cloud_llm = CloudLLMProvider()
