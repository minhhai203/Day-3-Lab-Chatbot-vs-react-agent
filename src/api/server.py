import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UI_DIR = PROJECT_ROOT / "ui"
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from src.agent.agent import ReActAgent
from src.chatbot.chatbot import SYSTEM_PROMPT, UniversityRegistrationChatbot
from src.core.gemini_provider import GeminiProvider
from src.core.llm_provider import LLMProvider
from src.core.local_provider import LocalProvider
from src.core.openai_provider import OpenAIProvider
from src.tools.course_registration_tools import get_course_registration_tools


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    mode: Literal["react", "baseline"] = "react"


class ChatResponse(BaseModel):
    mode: str
    answer: str
    trace: List[Dict[str, Any]]


app = FastAPI(title="CoursePilot API")
app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")


def build_llm() -> LLMProvider:
    provider = os.getenv("DEFAULT_PROVIDER", "").strip().lower()

    endpoint = os.getenv("LLM_ENDPOINT", "").strip()
    router_api_key = os.getenv("API_KEY", "").strip()
    router_model = os.getenv("MODEL", "").strip()
    if endpoint and router_api_key and router_model:
        return OpenAIProvider(
            model_name=router_model,
            api_key=router_api_key,
            base_url=endpoint,
        )

    if provider in {"google", "gemini"} or os.getenv("GEMINI_API_KEY"):
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", os.getenv("DEFAULT_MODEL", "gemini-1.5-flash"))
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini provider.")
        return GeminiProvider(model_name=model_name, api_key=api_key)

    if provider == "local":
        model_path = os.getenv("LOCAL_MODEL_PATH", "").strip()
        if not model_path:
            raise ValueError("LOCAL_MODEL_PATH is required for local provider.")
        return LocalProvider(model_path=model_path)

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
    model_name = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    if not api_key:
        raise ValueError(
            "No LLM credentials found. Set LLM_ENDPOINT + API_KEY + MODEL, "
            "or GEMINI_API_KEY, or OPENAI_API_KEY."
        )
    return OpenAIProvider(model_name=model_name, api_key=api_key)


def baseline_trace(chatbot: UniversityRegistrationChatbot, answer: str) -> List[Dict[str, Any]]:
    return [
        {
            "type": "system_prompt",
            "content": SYSTEM_PROMPT.strip(),
        },
        {
            "type": "user_prompt",
            "content": chatbot.last_prompt,
        },
        {
            "type": "tool_context",
            "content": chatbot.last_tool_context,
        },
        {
            "type": "final",
            "final_answer": answer,
        },
    ]


def run_baseline(message: str) -> ChatResponse:
    chatbot = UniversityRegistrationChatbot(llm=build_llm())
    answer = chatbot.chat(message)
    return ChatResponse(mode="baseline", answer=answer, trace=baseline_trace(chatbot, answer))


def run_react(message: str) -> ChatResponse:
    agent = ReActAgent(llm=build_llm(), tools=get_course_registration_tools(), max_steps=6)
    answer = agent.run(message)
    return ChatResponse(mode="react", answer=answer, trace=agent.latest_trace)


@app.get("/")
def index():
    return FileResponse(UI_DIR / "index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        if request.mode == "baseline":
            return run_baseline(request.message)
        return run_react(request.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
