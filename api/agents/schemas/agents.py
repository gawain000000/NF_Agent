from pydantic import BaseModel
from typing import Dict, Any, List


class Message(BaseModel):
    role: str
    content: str


class NodeState(BaseModel):
    state: Dict[str, Any]
    messages: List[Message]
    agent_workflow: List[str]
