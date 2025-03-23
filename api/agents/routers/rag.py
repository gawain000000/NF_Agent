import os
from typing import Literal
from typing_extensions import TypedDict
import logging

from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from NF_Agent.api.agents.schemas.agents import NodeState
from NF_Agent.api.agents.routers.utils import load_openapi_examples
from NF_Agent.services.rag import retrieval_milvus_BM25
from NF_Agent.core.config import PathSpec

router = APIRouter()
logging.basicConfig(level=logging.INFO)



script_dir = os.path.dirname(os.path.abspath(__file__))
openapi_examples = load_openapi_examples(os.path.join(script_dir, "openapi_examples/rag.yaml"))


@router.post(PathSpec.RAG)
async def rag_agent(
        request_body: Annotated[NodeState, Body(openapi_examples=openapi_examples)],
):
    state = request_body.state
    messages = request_body.messages
    agent_workflow = request_body.agent_workflow

    messages = [{"role": f"{msg.role}", "content": f"{msg.content}"} for msg in messages]

    rag_result = await retrieval_milvus_BM25(messages)
    agent_workflow.append("rag")
    agent_result = {"agent": "rag", "output": rag_result}
    state.append(agent_result)
    node_state = NodeState(state=state,
                           messages=messages,
                           agent_workflow=agent_workflow
                           )
    return node_state


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(load_openapi_examples(os.path.join(script_dir, "openapi_examples/rag.yaml")))
