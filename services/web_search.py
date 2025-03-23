import asyncio

from typing import List
from langchain_community.tools import DuckDuckGoSearchResults

search = DuckDuckGoSearchResults(output_format="list", num_results=5)


async def web_search(messages: List[dict]):
    search_query = messages[-1]["content"]
    search_res = await search.ainvoke(search_query)

    return search_res


if __name__ == '__main__':
    messages = [
        {"role": "user", "content": "What is the current status of the planning application on New Brent Street?"},
    ]
    asyncio.run(web_search(messages=messages))
