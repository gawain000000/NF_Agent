from fastapi import FastAPI
import uvicorn

from NF_Agent.api.agents.routers import web_search, rag

app = FastAPI()

api_prefix = "/api/v1"

app.include_router(router=web_search.router,
                   tags=["web_search_agent"],
                   prefix=api_prefix
                   )

app.include_router(router=rag.router,
                   tags=["rag_agent"],
                   prefix=api_prefix
                   )


def main():
    uvicorn.run(app="main:app", host="0.0.0.0", port=20009, reload=True, reload_includes=["*.json", "*.txt", "*.yaml"])


if __name__ == "__main__":
    main()
