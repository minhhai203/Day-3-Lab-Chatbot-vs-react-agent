import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent.agent_v1 import ReActAgentV1
from src.agent.agent_v2 import ReActAgentV2
from src.core.llm_provider import LLMProvider
from src.tools.course_registration_tools import get_course_registration_tools


class ScriptedLLM(LLMProvider):
    def __init__(self, model_name: str, responses: List[str]):
        super().__init__(model_name=model_name)
        self.responses = responses
        self.calls = 0

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if self.calls >= len(self.responses):
            content = "Final Answer: I ran out of scripted responses."
        else:
            content = self.responses[self.calls]
        self.calls += 1
        return {
            "content": content,
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
                "total_tokens": len(prompt.split()) + len(content.split()),
            },
            "latency_ms": 1,
            "provider": "scripted",
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None):
        yield self.generate(prompt, system_prompt)["content"]


def run() -> Dict[str, Any]:
    query = "Tôi muốn đăng ký môn AI và Data Science, kiểm tra còn chỗ không và học phí tổng cộng?"

    agent_v1 = ReActAgentV1(
        llm=ScriptedLLM(
            "agent-v1-success-scripted",
            [
                'Thought: I need official seat data first.\n'
                'Action: check_slots({"course_query": ["AI", "Data Science"]})',
                'Thought: I found available sections and now need the exact tuition.\n'
                'Action: get_tuition({"course_code": ["AI3010", "DATA3020"], "student_id": "2A202600713"})',
                'Thought: Tuition is clear, so I can register the selected sections.\n'
                'Action: register({"student_id": "2A202600713", "section_ids": ["AI3010-01", "DATA3020-02"], "confirm_payment": true})',
                "Thought: I have slot, tuition, and registration observations.\n"
                "Final Answer: AI3010-01 and DATA3020-02 were registered successfully. "
                "For student 2A202600713, the estimated total tuition and fees are 19,150,000 VND.",
            ],
        ),
        tools=get_course_registration_tools(),
        max_steps=5,
    )
    agent_v1_answer = agent_v1.run(query)

    agent_v1_failure = ReActAgentV1(
        llm=ScriptedLLM(
            "agent-v1-failure-trace",
            [
                'Thought: I will try a tool name that is not in the inventory.\n'
                'Action: search_course({"query": "AI"})',
                "Thought: The observation says TOOL_NOT_FOUND, so this is a failed trace for debugging.\n"
                "Final Answer: The first attempt failed because the agent hallucinated search_course. "
                "The fix is to use check_slots for availability.",
            ],
        ),
        tools=get_course_registration_tools(),
        max_steps=3,
    )
    agent_v1_failure_answer = agent_v1_failure.run("Check AI course availability.")

    agent_v2_recovery = ReActAgentV2(
        llm=ScriptedLLM(
            "agent-v2-recovery-trace",
            [
                'Thought: I will try a tool name that is not in the inventory.\n'
                'Action: search_course({"query": "AI"})',
                "Thought: The observation says TOOL_NOT_FOUND and lists available tools, "
                "so I should use check_slots.\n"
                'Action: check_slots({"course_query": "AI"})',
                "Thought: I now have official availability and can answer safely.\n"
                "Final Answer: AI3010 has an available section, so the correct recovery "
                "after the failed tool call is to use check_slots.",
            ],
        ),
        tools=get_course_registration_tools(),
        max_steps=4,
    )
    agent_v2_recovery_answer = agent_v2_recovery.run("Check AI course availability.")

    return {
        "cases": [
            {
                "name": "agent_v1_success",
                "query": query,
                "agent_version": "v1",
                "answer": agent_v1_answer,
                "uses_tools": True,
                "tools": ["check_slots", "get_tuition", "register"],
                "success": "registered successfully" in agent_v1_answer and "19,150,000 VND" in agent_v1_answer,
            },
            {
                "name": "agent_v1_failure_trace",
                "query": "Check AI course availability.",
                "agent_version": "v1",
                "answer": agent_v1_failure_answer,
                "uses_tools": True,
                "success": False,
                "reason": "Intentional hallucinated tool call demonstrates failure analysis.",
            },
            {
                "name": "agent_v2_recovery_trace",
                "query": "Check AI course availability.",
                "agent_version": "v2",
                "answer": agent_v2_recovery_answer,
                "uses_tools": True,
                "tools": ["search_course_failed", "check_slots"],
                "success": "AI3010" in agent_v2_recovery_answer and "check_slots" in agent_v2_recovery_answer,
                "trace": agent_v2_recovery.latest_trace,
                "reason": "V2 exposes available_tools in observations and records a structured trace.",
            },
        ]
    }


if __name__ == "__main__":
    summary = run()
    output_path = Path("report/group_report/evaluation_summary.json")
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nSaved summary to {output_path}")
