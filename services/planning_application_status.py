import os
import json
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI

from NF_Agent.services.utils import update_system_prompt, restrict_to_json_format
from NF_Agent.core.config import chat_llm_settings, embedding_model_settings, agent_settings, milvus_settings

mongodb_client = AsyncIOMotorClient(agent_settings.MONGODB_URI)
db = mongodb_client[agent_settings.MONGODB_DB_NAME]
coll = db[agent_settings.MONGODB_COLL_NAME]

chat_llm_client = AsyncOpenAI(base_url=chat_llm_settings.CHAT_LLM_BASE_URL,
                              api_key=chat_llm_settings.CHAT_LLM_API_KEY
                              )

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
with open(os.path.join(parent_dir,
                       "api/agents/routers/prompts/planning_application_status/parameters_identification.txt")) as f:
    parameters_identification_prompt = f.read()

with open(os.path.join(parent_dir,
                       "api/agents/routers/prompts/planning_application_status/answer_user_query.txt")) as f:
    answer_user_query_prompt = f.read()


async def answer_user_query(user_query, query_result):
    task_prompt = answer_user_query_prompt.format(querying_result=query_result,
                                                  user_query=user_query
                                                  )
    task_messages = [{"role": "user", "content": task_prompt}]
    response = await chat_llm_client.chat.completions.create(model=chat_llm_settings.CHAT_LLM_MODEL,
                                                             messages=task_messages,
                                                             stream=False,
                                                             temperature=chat_llm_settings.temperature,
                                                             top_p=chat_llm_settings.top_p
                                                             )
    response = response.choices[0].message.content
    return response


async def parameters_identification(messages):
    task_messages = update_system_prompt(messages=messages, system_prompt=parameters_identification_prompt)
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


async def planning_application_status_checking(messages):
    params = await parameters_identification(messages)

    borough = params["borough"]
    status = params["status"]
    all_borough = await coll.distinct("borough")
    if borough in all_borough:
        query = {"borough": borough, "status": status}
        res = await coll.find(query, {"_id": 0, "borough": 1, "status": 1}).to_list(length=None)
        count = len(res)
        res = {"borough": borough, "status": status, "count": count, "valid": True}

    else:
        res = {"borough": borough, "valid": False}

    final_res = await answer_user_query(user_query=messages[-1]["content"], query_result=res)

    return final_res


if __name__ == '__main__':
    # messages = [
    #     {"role": "user",
    #      "content": "How many planning applications have been approved in the London Borough of Barnet?"},
    # ]
    messages = [
        {"role": "user",
         "content": "How many planning applications have been approved in the Hong Kong?"},
    ]
    asyncio.run(planning_application_status_checking(messages=messages))
