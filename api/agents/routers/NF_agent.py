import os
import logging

from typing import Annotated, Optional
from fastapi import APIRouter, Body
from pydantic import BaseModel
from openai import AsyncOpenAI
from sse_starlette.sse import EventSourceResponse

from NF_Agent.api.agents.routers.utils import load_openapi_examples, async_stream_generator
from NF_Agent.core.config import PathSpec, chat_llm_settings
from NF_Agent.services.utils import update_system_prompt
from NF_Agent.services.agent_architecture import NF_agent
from NF_Agent.api.agents.schemas.agents import NodeState

router = APIRouter()
logging.basicConfig(level=logging.INFO)

script_dir = os.path.dirname(os.path.abspath(__file__))
openapi_examples = load_openapi_examples(os.path.join(script_dir, "openapi_examples/NF_agent.yaml"))

with open(os.path.join(script_dir, "prompts/generation/generation.txt")) as f:
    generation_system_prompt = f.read()

chat_llm_client = AsyncOpenAI(base_url=chat_llm_settings.CHAT_LLM_BASE_URL,
                              api_key=chat_llm_settings.CHAT_LLM_API_KEY)


class Message(BaseModel):
    role: str
    content: str


class AgentChatCompletion(BaseModel):
    messages: list[Message]
    stream: bool = True


@router.post(PathSpec.NF_AGENT)
async def nf_agent_generation(
        request_body: Annotated[AgentChatCompletion, Body(openapi_examples=openapi_examples)]
):
    messages = request_body.messages
    stream = request_body.stream

    messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    graph_state = NodeState(state=[],
                            messages=messages,
                            agent_workflow=[]
                            )
    agent_response = await NF_agent.ainvoke(graph_state.model_dump())
    generation_prompt = generation_system_prompt + "\n" + str(agent_response["state"][-1])
    generation_messages = update_system_prompt(messages=messages, system_prompt=generation_prompt)
    response = await chat_llm_client.chat.completions.create(model=chat_llm_settings.CHAT_LLM_MODEL,
                                                             messages=generation_messages,
                                                             stream=stream,
                                                             temperature=chat_llm_settings.temperature,
                                                             top_p=chat_llm_settings.top_p
                                                             )

    # Handle streamed responses
    if stream:
        return EventSourceResponse(async_stream_generator(response))

    # Handle non-streamed response
    return response
