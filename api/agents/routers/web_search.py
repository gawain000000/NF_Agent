import os
from typing import Annotated
import logging

from fastapi import APIRouter, Body

from NF_Agent.api.agents.schemas.agents import NodeState
from NF_Agent.api.agents.routers.utils import load_openapi_examples
from NF_Agent.services.web_search import web_search

router = APIRouter()
logging.basicConfig(level=logging.INFO)


class PathSpec:
    SUPERVISOR: str = "/agent/web_search"


script_dir = os.path.dirname(os.path.abspath(__file__))
openapi_examples = load_openapi_examples(os.path.join(script_dir, "openapi_examples/web_search.yaml"))


@router.post(PathSpec.SUPERVISOR)
async def web_search_agent(
        request_body: Annotated[NodeState, Body(openapi_examples=openapi_examples)],
):
    state = request_body.state
    messages = request_body.messages
    agent_workflow = request_body.agent_workflow

    messages = [{"role": f"{msg.role}", "content": f"{msg.content}"} for msg in messages]
    web_search_result = await web_search(messages)
    agent_workflow.append("web_search_result")
    agent_result = {"agent": "web_search", "output": web_search_result}
    state.append(agent_result)
    node_state = NodeState(state=state,
                           messages=messages,
                           agent_workflow=agent_workflow
                           )
    return node_state


if __name__ == '__main__':
    print(openapi_examples)
