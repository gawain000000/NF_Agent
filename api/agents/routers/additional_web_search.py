import os
from typing import Annotated
import logging

from fastapi import APIRouter, Body

from NF_Agent.api.agents.schemas.agents import NodeState
from NF_Agent.api.agents.routers.utils import load_openapi_examples
from NF_Agent.services.additional_web_search import additional_web_search
from NF_Agent.core.config import PathSpec

router = APIRouter()
logging.basicConfig(level=logging.INFO)

script_dir = os.path.dirname(os.path.abspath(__file__))
openapi_examples = load_openapi_examples(os.path.join(script_dir, "openapi_examples/additional_web_search.yaml"))


@router.post(PathSpec.ADDITIONAL_WEB_SEARCH)
async def web_search_agent(
        request_body: Annotated[NodeState, Body(openapi_examples=openapi_examples)]
):
    state = request_body.state
    messages = request_body.messages
    agent_workflow = request_body.agent_workflow

    messages = [{"role": f"{msg.role}", "content": f"{msg.content}"} for msg in messages]
    latest_state = state[-1]
    additional_web_search_result = await additional_web_search(agents_execution_result=latest_state,
                                                               messages=messages)
    agent_workflow.append("additional_web_search")
    state[-1] = additional_web_search_result
    node_state = NodeState(state=state,
                           messages=messages,
                           agent_workflow=agent_workflow
                           )
    return node_state
