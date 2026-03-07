import os
import httpx
from openai import AsyncOpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMRouter")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

KIMI_API_KEY = os.getenv("KIMI_API_KEY", "dummy_key")
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
KIMI_MODEL = os.getenv("KIMI_MODEL", "moonshot-v1-8k")

class IntelligentRouter:
    def __init__(self):
        self.kimi_client = AsyncOpenAI(api_key=KIMI_API_KEY, base_url=KIMI_BASE_URL)
        
    def _determine_complexity(self, prompt: str) -> str:
        """
        Intelligently routes based on task requirements:
        - Deep reasoning, vast context (e.g. evaluating 10 URLs), or strict financial math -> 'high' (Cloud)
        - Basic greetings, simple CRM Q&A, text formatting -> 'low' (Local)
        """
        high_complexity_keywords = [
            "analyze", "evaluate", "compare", "projection", "strategic", 
            "negotiate bulk", "contract", "summary"
        ]
        
        # Immediate fallback for huge context limits
        if len(prompt) > 2000:
            return "high"
            
        for kw in high_complexity_keywords:
            if kw in prompt.lower():
                return "high"
                
        return "low"

    async def generate_response(self, system_prompt: str, user_prompt: str, force_cloud: bool = False):
        complexity = "high" if force_cloud else self._determine_complexity(user_prompt)
        
        if complexity == "high":
            logger.info("Task complexity HIGH or CLOUD forced. Routing to Kimi K2.5 (Cloud).")
            return await self._call_kimi(system_prompt, user_prompt)
            
        logger.info(f"Task complexity LOW. Routing to Local Ollama ({OLLAMA_MODEL}).")
        try:
            return await self._call_ollama(system_prompt, user_prompt)
        except Exception as e:
            logger.warning(f"Local Ollama failed ({e}). Escalating to Kimi K2.5 fallback...")
            return await self._call_kimi(system_prompt, user_prompt)

    async def _call_ollama(self, system: str, prompt: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                },
                timeout=15.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")

    async def _call_kimi(self, system: str, prompt: str):
        if KIMI_API_KEY == "dummy_key":
            return "[Escalated to Cloud (Mock)]: Kimi K2.5 would process this complex request. API key required."
            
        completion = await self.kimi_client.chat.completions.create(
            model=KIMI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return completion.choices[0].message.content

router = IntelligentRouter()
