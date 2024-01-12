from fastapi import Depends, FastAPI
from typing import cast, Annotated, AsyncIterator
from docker.client import DockerClient
from docker.errors import ContainerError
from pydantic import BaseModel
import logging

from clickhouse_format_service.docker_image import (
    DockerImage,
    yield_from_built_images,
    CH_DOCKER,
)

app = FastAPI(title="Clickhouse Format Service", version="0.1.0")


async def get_docker_client() -> AsyncIterator[DockerClient]:
    """context manager for docker client that ensures its closure after use. Meant
    to be used with dependency-injection in FastAPI via `Depends`"""
    client = DockerClient.from_env()
    try:
        yield client
    finally:
        client.close()


INJECTED_DOCKER_CLIENT = Annotated[DockerClient, Depends(get_docker_client)]


@app.get("/")
async def get_current_docker_info(client: INJECTED_DOCKER_CLIENT) -> list[DockerImage]:
    """Return clickhouse version and docker image info"""

    return [
        cast(DockerImage, image.attrs)
        async for image in yield_from_built_images("", client)
    ]


class SQL(BaseModel):
    sql: str


@app.post("/")
async def clickhouse_format_sql(sql: str, client: INJECTED_DOCKER_CLIENT) -> str:
    """Get the first image matching the name or build the image if it does not exist,
    then run the container for that image feeding the input in and returning the container
    output"""
    logging.getLogger("uvicorn.error").debug(f"received SQL: {sql}")

    try:
        output = client.containers.run(
            CH_DOCKER,
            entrypoint=["clickhouse", "format", "--quiet", "--multiquery", "--query"],
            command=f"'{sql}'",
            remove=True,
        )
    except ContainerError as e:
        logging.getLogger("uvicorn.error").debug(
            f"Command '{e.command}' in image '{e.image}' "
            f"returned non-zero exit status {e.exit_status}{e.stderr}"
        )
        output = e.stderr

    if isinstance(output, bytes):
        return output.decode("utf-8")
    elif isinstance(output, str):
        return output

    raise TypeError(f"container output is not bytes/str: {output}")
