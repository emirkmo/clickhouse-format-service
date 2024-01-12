from fastapi import Depends, FastAPI
from typing import cast, Annotated, AsyncIterator
from docker.models.images import Image
from docker.client import DockerClient
from docker.errors import ImageLoadError, ImageNotFound
from pydantic import BaseModel
import logging

from clickhouse_format_service.docker_image import (
    IMAGE_NAME,
    DockerImage,
    yield_from_built_images,
    build_clickhouse_format_docker_image,
)

app = FastAPI()


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
    """Return docker image information for all clickhouse-format-docker images."""
    return [
        cast(DockerImage, image.attrs)
        async for image in yield_from_built_images(IMAGE_NAME, client)
    ]


class SQL(BaseModel):
    sql: str

@app.post("/")
async def clickhouse_format_sql(sql: SQL, client: INJECTED_DOCKER_CLIENT) -> str:
    """Get the first image matching the name or build the image if it does not exist,
    then run the container for that image feeding the input in and returning the container
    output"""
    try:
        image = cast(Image, client.images.get(IMAGE_NAME))
    except (ImageNotFound, ImageLoadError):
        image = await build_clickhouse_format_docker_image(client)

    logging.info("Found image {}", image)

    logging.info(f"received SQL{sql}")

    output = client.containers.run(IMAGE_NAME, "SELECT 1;")
    if isinstance(output, bytes):
        return str(output)
    return str(output)
