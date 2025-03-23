import os
import asyncio

from typing import List
from langchain_community.tools import DuckDuckGoSearchResults
from openai import AsyncOpenAI

from core.config import chat_llm_settings
from services.utils import update_system_prompt

search = DuckDuckGoSearchResults(output_format="list", num_results=5)

chat_llm_client = AsyncOpenAI(base_url=chat_llm_settings.CHAT_LLM_BASE_URL,
                              api_key=chat_llm_settings.CHAT_LLM_API_KEY
                              )

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
with open(os.path.join(parent_dir,
                       "api/agents/routers/prompts/additional_web_search/web_search_decision.txt")) as f:
    web_search_decision_prompt = f.read()


async def additional_web_search_decision(agents_execution_result, messages: List[dict]):
    task_prompt = web_search_decision_prompt.format(agents_execution_result=agents_execution_result
                                                    )
    task_messages = update_system_prompt(messages=messages, system_prompt=task_prompt)
    response = await chat_llm_client.chat.completions.create(model=chat_llm_settings.CHAT_LLM_MODEL,
                                                             messages=task_messages,
                                                             stream=False,
                                                             temperature=chat_llm_settings.temperature,
                                                             top_p=chat_llm_settings.top_p
                                                             )
    response = response.choices[0].message.content
    return response

if __name__ == '__main__':
    asyncio.run(additional_web_search_decision)
