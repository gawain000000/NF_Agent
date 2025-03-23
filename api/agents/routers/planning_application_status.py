import os
from typing import Literal
from typing_extensions import TypedDict
import logging

from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from NF_Agent.api.agents.schemas.agents import NodeState
from NF_Agent.api.agents.routers.utils import load_openapi_examples
from NF_Agent.services.planning_application_status import planning_application_status_checking
from NF_Agent.core.config import PathSpec

router = APIRouter()
logging.basicConfig(level=logging.INFO)

script_dir = os.path.dirname(os.path.abspath(__file__))
openapi_examples = load_openapi_examples(os.path.join(script_dir, "openapi_examples/planning_status_checking.yaml"))


@router.post(PathSpec.DB_QUERY)
async def db_query_agent(
        request_body: Annotated[NodeState, Body(openapi_examples=openapi_examples)],
):
    state = request_body.state
    messages = request_body.messages
    agent_workflow = request_body.agent_workflow

    messages = [{"role": f"{msg.role}", "content": f"{msg.content}"} for msg in messages]

    result = await planning_application_status_checking(messages)

    agent_workflow.append("db_query")
    agent_result = {"agent": "db_query", "output": result}
    state.append(agent_result)
    node_state = NodeState(state=state,
                           messages=messages,
                           agent_workflow=agent_workflow
                           )
    return node_state
