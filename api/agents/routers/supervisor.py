import os
import logging

from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from NF_Agent.api.agents.schemas.agents import NodeState
from NF_Agent.api.agents.routers.utils import load_openapi_examples
from NF_Agent.services.supervisor import agent_selection
from NF_Agent.core.config import PathSpec

router = APIRouter()
logging.basicConfig(level=logging.INFO)

script_dir = os.path.dirname(os.path.abspath(__file__))
openapi_examples = load_openapi_examples(os.path.join(script_dir, "openapi_examples/supervisor.yaml"))


@router.post(PathSpec.SUPERVISOR)
async def supervisor(
        request_body: Annotated[NodeState, Body(openapi_examples=openapi_examples)],
):
    state = request_body.state
    messages = request_body.messages
    agent_workflow = request_body.agent_workflow

    messages = [{"role": f"{msg.role}", "content": f"{msg.content}"} for msg in messages]
    result = await agent_selection(messages=messages)
    agent_workflow.append("supervisor")
    supervisor_result = {"agent": "supervisor", "output": result}
    state.append(supervisor_result)
    node_state = NodeState(state=state,
                           messages=messages,
                           agent_workflow=agent_workflow
                           )
    return node_state


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(load_openapi_examples(os.path.join(script_dir, "openapi_examples/supervisor.yaml")))
