from tavily import TavilyClient
from core.config import agent_settings

search_query = "What is the current status of the planning application on New Brent Street?"

tavily_client = TavilyClient(api_key=agent_settings.TAVILY_TOKEN)

qna_search_result = tavily_client.qna_search(query=search_query,
                                             search_depth="advanced",
                                             max_results=5
                                             )

search_result = tavily_client.search(query=search_query,
                                     search_depth="advanced",
                                     max_results=5,
                                     include_answers=True,
                                     include_raw_content=True
                                     )

print(search_result["answer"])
print(search_result["results"][0]["content"])

print("=" * 100)
print(qna_search_result)
