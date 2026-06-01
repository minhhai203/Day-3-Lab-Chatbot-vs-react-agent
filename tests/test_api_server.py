from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient

from src.api import server
from src.core.llm_provider import LLMProvider


class ScriptedLLM(LLMProvider):
    def __init__(self, responses: List[str]):
        super().__init__(model_name="api-test-llm")
        self.responses = responses
        self.calls = 0

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        content = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        return {
            "content": content,
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            "latency_ms": 1,
            "provider": "test",
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None):
        yield self.generate(prompt, system_prompt)["content"]


def test_api_serves_health_and_index():
    client = TestClient(server.app)

    assert client.get("/health").json() == {"ok": True}
    assert "CoursePilot" in client.get("/").text


def test_api_chat_baseline_returns_answer_and_trace(monkeypatch):
    monkeypatch.setattr(server, "build_llm", lambda: ScriptedLLM(["Baseline answer"]))
    client = TestClient(server.app)

    response = client.post(
        "/chat",
        json={"message": "AI còn chỗ không?", "mode": "baseline"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Baseline answer"
    assert payload["mode"] == "baseline"
    assert any(item["type"] == "tool_context" for item in payload["trace"])


def test_api_chat_react_returns_agent_trace(monkeypatch):
    monkeypatch.setattr(
        server,
        "build_llm",
        lambda: ScriptedLLM(
            [
                'Thought: Need slots.\nAction: check_slots({"course_query":"AI"})',
                "Thought: Done.\nFinal Answer: AI3010 has available seats.",
            ]
        ),
    )
    client = TestClient(server.app)

    response = client.post(
        "/chat",
        json={"message": "AI còn chỗ không?", "mode": "react"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "AI3010" in payload["answer"]
    assert payload["mode"] == "react"
    assert any(item["type"] == "step" for item in payload["trace"])
