import json
import time
from typing import Dict, Any, Optional, Generator

import requests

from src.core.llm_provider import LLMProvider


class LocalProvider(LLMProvider):
    """
    Local LLM provider backed by Ollama.
    """

    def __init__(
        self,
        model_name: str = "phi3:latest",
        base_url: str = "http://127.0.0.1:11434",
        timeout: int = 120,
    ):
        super().__init__(model_name=model_name)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
        }

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        latency_ms = int((time.time() - start_time) * 1000)
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        return {
            "content": data.get("response", "").strip(),
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "latency_ms": latency_ms,
            "provider": "ollama",
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": True,
        }

        with requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
            stream=True,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                chunk = json.loads(line)
                token = chunk.get("response", "")
                if token:
                    yield token
