from fastapi import FastAPI
import uvicorn

from NF_Agent.api.agents.routers import (
    supervisor, web_search, rag, planning_application_status, agent_execution, \
    additional_web_search, NF_agent
)
from NF_Agent.core.config import agent_settings

app = FastAPI()

app.include_router(router=supervisor.router,
                   tags=["supervisor"],
                   prefix=agent_settings.API_PREFIX
                   )

app.include_router(router=web_search.router,
                   tags=["web_search_agent"],
                   prefix=agent_settings.API_PREFIX
                   )

app.include_router(router=rag.router,
                   tags=["rag_agent"],
                   prefix=agent_settings.API_PREFIX
                   )

app.include_router(router=planning_application_status.router,
                   tags=["db_query_agent"],
                   prefix=agent_settings.API_PREFIX
                   )

app.include_router(router=additional_web_search.router,
                   tags=["additional_web_search"],
                   prefix=agent_settings.API_PREFIX
                   )

app.include_router(router=agent_execution.router,
                   tags=["agent_execution"],
                   prefix=agent_settings.API_PREFIX
                   )

app.include_router(router=NF_agent.router,
                   tags=["NF_agent"],
                   prefix=agent_settings.API_PREFIX
                   )


def main():
    uvicorn.run(app="main:app", host="0.0.0.0", port=20009, reload=True, reload_includes=["*.json", "*.txt", "*.yaml"])


if __name__ == "__main__":
    main()
