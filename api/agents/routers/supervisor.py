import os
from typing import Literal
from typing_extensions import TypedDict
import logging

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from api.agents.schemas.agents import NodeState
from api.agents.routers.utils import load_openapi_examples

router = APIRouter()
logging.basicConfig(level=logging.INFO)


class PathSpec:
    SUPERVISOR: str = "/agent/supervisor"


# @router.post(PathSpec.SUPERVISOR)
# async def supervisor(
#         request_body: Annotated[NodeState, load_openapi_examples()],
# ):
#     ...

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(load_openapi_examples(os.path.join(script_dir, "openapi_examples/supervisor.yaml")))
