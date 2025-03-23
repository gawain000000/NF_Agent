import os
import json
import asyncio

from openai import AsyncOpenAI
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

from core.config import chat_llm_settings
from services.utils import update_system_prompt, restrict_to_json_format

### temp load prompt
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
with open(os.path.join(parent_dir, "api/agents/routers/prompts/supervisor/rag_decision.txt")) as f:
    rag_decision = f.read()
with open(os.path.join(parent_dir, "api/agents/routers/prompts/supervisor/initial_web_search_decision.txt")) as f:
    initial_web_search = f.read()
with open(os.path.join(parent_dir, "api/agents/routers/prompts/supervisor/database_query_decision.txt")) as f:
    database_query_decision = f.read()
with open(os.path.join(parent_dir, "api/agents/routers/prompts/supervisor/additional_web_search_decision.txt")) as f:
    additional_web_search_decision = f.read()

agent_determination_prompts = {
    "rag": rag_decision,
    "initial_web_search": initial_web_search,
    "database_query_decision": database_query_decision,
    "additional_web_search_decision": additional_web_search_decision,
}

chat_llm_client = AsyncOpenAI(base_url=chat_llm_settings.CHAT_LLM_BASE_URL,
                              api_key=chat_llm_settings.CHAT_LLM_API_KEY
                              )


async def agent_selection(messages: List[dict]):
    agents = ["rag", "initial_web_search", "database_query_decision"]
    tasks = [determine_use_of_agent(messages=messages, agent=agent) for agent in agents]
    results_list = await asyncio.gather(*tasks)
    results_dict = dict(zip(agents, results_list))
    return results_dict


async def determine_use_of_agent(messages: List[dict], agent: str):
    system_prompt = agent_determination_prompts[agent]
    task_messages = update_system_prompt(messages=messages, system_prompt=system_prompt)
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


if __name__ == '__main__':
    # print(agent_determination_prompts)
    messages = [
        {"role": "user", "content": "What is the current status of the planning application on New Brent Street?"},
    ]
    asyncio.run(agent_selection(messages=messages))
