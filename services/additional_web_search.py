import os
import json
import asyncio

from typing import List
from langchain_community.tools import DuckDuckGoSearchResults
from openai import AsyncOpenAI

from NF_Agent.core.config import chat_llm_settings
from NF_Agent.services.utils import update_system_prompt, restrict_to_json_format

search = DuckDuckGoSearchResults(output_format="list", num_results=5)

chat_llm_client = AsyncOpenAI(base_url=chat_llm_settings.CHAT_LLM_BASE_URL,
                              api_key=chat_llm_settings.CHAT_LLM_API_KEY
                              )

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
with open(os.path.join(parent_dir,
                       "api/agents/routers/prompts/additional_web_search/web_search_decision.txt")) as f:
    web_search_decision_prompt = f.read()


async def web_search(search_query):
    search_res = await search.ainvoke(search_query)
    return search_res


async def additional_web_search_decision(agents_execution_result, messages: List[dict]):
    task_prompt = web_search_decision_prompt + "\n\n" + f"Ageent Information:\n{str(agents_execution_result)}"
    task_messages = update_system_prompt(messages=messages, system_prompt=task_prompt)
    response = await chat_llm_client.chat.completions.create(model=chat_llm_settings.CHAT_LLM_MODEL,
                                                             messages=task_messages,
                                                             stream=False,
                                                             temperature=chat_llm_settings.temperature,
                                                             top_p=chat_llm_settings.top_p
                                                             )

    try:
        result = json.loads(response.choices[0].message.content)
    except:
        response = await restrict_to_json_format(llm_client=chat_llm_client,
                                                 llm_settings=chat_llm_settings,
                                                 messages=task_messages
                                                 )
        result = json.loads(response.choices[0].message.content)

    return result


async def additional_web_search(agents_execution_result, messages: List[dict]):
    decision = await additional_web_search_decision(agents_execution_result=agents_execution_result,
                                                    messages=messages
                                                    )
    if decision["additional_web_search"]:
        search_result = await web_search(search_query=decision["search_query"])
        agents_execution_result["output"].append({"agent": "additional_web_search",
                                                  "decision": decision,
                                                  "output": search_result})
    return agents_execution_result


if __name__ == '__main__':
    agent_execution_result = {"agent": "agent_execution",
                              "output": [
                                  {
                                      "agent": "db_query",
                                      "output": "No data"
                                  }
                              ]
                              }
    messages = [
        {
            "role": "system",
            "content": "You are AI assistant response for answering the question of planning application in London"
        },
        {
            "role": "user",
            "content": "How many planning applications have been approved in the Hong Kong?"
        }
    ]
    asyncio.run(additional_web_search(agents_execution_result=agent_execution_result,
                                      messages=messages
                                      ))
