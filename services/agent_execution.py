import os
import json
import asyncio
from typing import List
import aiohttp

from NF_Agent.core.config import PathSpec, agent_settings
from NF_Agent.api.agents.schemas.agents import NodeState

url_format = "http://{host}:{port}{route}"

agent_routes = {
    "rag": url_format.format(
        host=agent_settings.HOST,
        port=agent_settings.PORT,
        route=agent_settings.API_PREFIX + PathSpec.RAG
    ),
    "web_search": url_format.format(
        host=agent_settings.HOST,
        port=agent_settings.PORT,
        route=agent_settings.API_PREFIX + PathSpec.WEB_SEARCH
    ),
    "db_query": url_format.format(
        host=agent_settings.HOST,
        port=agent_settings.PORT,
        route=agent_settings.API_PREFIX + PathSpec.DB_QUERY
    )
}


async def execute_single_agent(node_state: NodeState, agent: str):
    async with aiohttp.ClientSession() as session:
        # Convert node_state to a serializable dictionary
        node_state_dict = node_state.dict() if hasattr(node_state, "dict") else node_state
        async with session.post(url=agent_routes[agent], json=node_state_dict) as response:
            res = await response.json()
    return res


async def execute_agents(execution_decision, node_state: NodeState):
    task_list = []
    execution_decision = execution_decision["output"]
    for agent_decision in execution_decision.keys():
        print(execution_decision[agent_decision])
        if execution_decision[agent_decision]["execute"]:
            task_list.append(
                execute_single_agent(node_state=node_state, agent=agent_decision)
            )
    print("=" * 100)
    print(task_list)
    results = await asyncio.gather(*task_list)
    execution_result = []
    for result in results:
        agent_state = result["state"][-1]
        execution_result.append(agent_state)
    return execution_result


if __name__ == '__main__':
    execution_decision = {
        "rag": {
            "execute": False,
            "search_document": []
        },
        "web_search": {
            "execute": True,
            "query": "current status of planning application on New Brent Street London"
        },
        "db_query": {
            "execute": True
        }
    }

    node_state = {
        "state": [],
        "messages": [
            {
                "role": "user",
                "content": "How many planning applications have been approved in the London Borough of Barnet?"
            },
        ],
        "agent_workflow": ["supervisor"]
    }

    asyncio.run(execute_agents(execution_decision=execution_decision, node_state=node_state))
