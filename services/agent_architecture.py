import asyncio
import aiohttp

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Any, Dict

from NF_Agent.core.config import agent_settings, PathSpec
from NF_Agent.api.agents.schemas.agents import NodeState


class GraphState(TypedDict):
    state: List[Dict[str, Any]]
    messages: List[Any]
    agent_workflow: List[str]


url_format = "http://{host}:{port}{route}"
host = "127.0.0.1"

nodes_url = {
    "supervisor": url_format.format(
        host=host,
        port=agent_settings.PORT,
        route=agent_settings.API_PREFIX + PathSpec.SUPERVISOR
    ),
    "agents_execution": url_format.format(
        host=host,
        port=agent_settings.PORT,
        route=agent_settings.API_PREFIX + PathSpec.AGENTS_EXECUTION
    ),
    "additional_web_search": url_format.format(
        host=host,
        port=agent_settings.PORT,
        route=agent_settings.API_PREFIX + PathSpec.ADDITIONAL_WEB_SEARCH
    )
}


async def request_node(state: dict, node_name: str) -> dict:
    """
    Sends an asynchronous POST request to the specified node route with the given state.

    :param state: The state dictionary to send as JSON.
    :param node_name: The node name for the request.
    :return: JSON response from the node.
    :raises RuntimeError: If the request fails.
    """
    url = nodes_url.get(node_name)
    if not url:
        raise ValueError(f"Node URL for '{node_name}' not found in configuration.")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url=url, json=state) as response:
                response.raise_for_status()  # Raise exception for bad responses
                return await response.json()
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Request to node '{node_name}' failed: {e}")


async def process_node(state: dict, node_name: str) -> dict:
    """
    Generic async function to process requests for different nodes.

    :param state: The state dictionary to send.
    :param node_name: The name of the node to request.
    :return: JSON response from the node.
    """
    print("=" * 100)
    print(state)
    return await request_node(state, node_name)


async def supervisor_node(state: dict) ->dict:
    return await process_node(state, node_name="supervisor")


async def agents_execution_node(state: dict) -> dict:
    return await process_node(state, node_name="agents_execution")


async def additional_web_search_node(state: dict) -> dict:
    return await process_node(state, node_name="additional_web_search")


NF_agent_framework = StateGraph(GraphState)
NF_agent_framework.add_node(node="supervisor", action=supervisor_node)
NF_agent_framework.add_node(node="agents_execution", action=agents_execution_node)
NF_agent_framework.add_node(node="additional_web_search", action=additional_web_search_node)

NF_agent_framework.add_edge(start_key=START, end_key="supervisor")
NF_agent_framework.add_edge(start_key="supervisor", end_key="agents_execution")
NF_agent_framework.add_edge(start_key="agents_execution", end_key="additional_web_search")
NF_agent_framework.add_edge(start_key="additional_web_search", end_key=END)

NF_agent = NF_agent_framework.compile()

if __name__ == '__main__':
    graph_state = {
        "state": [],
        "messages": [
            {"role": "user", "content": "What is the current status of the planning application on New Brent Street?"},
        ],
        "agent_workflow": [],
    }

    async def main():
        # Use the asynchronous API (ainvoke) to call the agent
        # result = await NF_agent.ainvoke(graph_state)
        result = await request_node(state=graph_state, node_name="supervisor")
        print(result)

    asyncio.run(main())
