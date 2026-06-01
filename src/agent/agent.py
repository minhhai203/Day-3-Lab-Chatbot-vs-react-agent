"""
Default ReAct agent entrypoint.

`ReActAgent` points to V2 so existing imports keep working, while the lab can
compare V1 and V2 explicitly through `agent_v1.py` and `agent_v2.py`.
"""
from src.agent.agent_v1 import ReActAgentV1
from src.agent.agent_v2 import ReActAgentV2


ReActAgent = ReActAgentV2

__all__ = ["ReActAgent", "ReActAgentV1", "ReActAgentV2"]
