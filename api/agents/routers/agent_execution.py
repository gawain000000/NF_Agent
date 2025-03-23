import os
import logging

from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from NF_Agent.api.agents.schemas.agents import NodeState
from NF_Agent.api.agents.routers.utils import load_openapi_examples
from NF_Agent.core.config import PathSpec
from NF_Agent.services.agent_execution import execute_agents

router = APIRouter()
logging.basicConfig(level=logging.INFO)

script_dir = os.path.dirname(os.path.abspath(__file__))
openapi_examples = load_openapi_examples(os.path.join(script_dir, "openapi_examples/agents_execution.yaml"))


@router.post(PathSpec.AGENTS_EXECUTION)
async def agents_execution(
        request_body: Annotated[NodeState, Body(openapi_examples=openapi_examples)]
):
    state = request_body.state
    messages = request_body.messages
    agent_workflow = request_body.agent_workflow

    messages = [{"role": f"{msg.role}", "content": f"{msg.content}"} for msg in messages]
    execution_decision = state[-1]
    temp_node_state = NodeState(
        state=state,
        messages=messages,
        agent_workflow=agent_workflow
    )
    result = await execute_agents(execution_decision=execution_decision, node_state=temp_node_state)
    agent_workflow.append("agents_execution")
    agent_execution_result = {"agent": "supervisor", "output": result}
    state.append(agent_execution_result)
    node_state = NodeState(state=state,
                           messages=messages,
                           agent_workflow=agent_workflow
                           )
    return node_state
