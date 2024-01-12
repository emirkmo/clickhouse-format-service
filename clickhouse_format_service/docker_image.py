from typing import cast, AsyncIterator
from collections import namedtuple
from docker.models.images import Image
from docker.client import DockerClient

IMAGE_NAME = "clickhouse-format-docker:latest"
DEFAULT_VERSION = "23.11.3.23"
DOCKERFILE_PATH = "clickhouse-format-docker/Dockerfile"

DockerImage = namedtuple(
    typename="DockerImage",
    field_names=[
        "Id",
        "RepoTags",
        "RepoDigests",
        "Parent",
        "Comment",
        "Created",
        "Container",
        "ContainerConfig",
        "DockerVersion",
        "Author",
        "Config",
        "Architecture",
        "Os",
        "Size",
        "VirtualSize",
        "GraphDriver",
        "RootFS",
        "Metadata",
    ],
)


async def yield_from_built_images(
    image_name: str, client: DockerClient
) -> AsyncIterator[Image]:
    """Yield matching image names from built images"""
    images = cast(list[Image], client.images.list())
    for image in images:
        if image_name in str(image):
            yield image

async def build_clickhouse_format_docker_image(
    client: DockerClient, version: str = DEFAULT_VERSION
) -> Image:
    """Build the clickhouse format docker image and return it"""
    with open(DOCKERFILE_PATH) as dockerfile:
        image = client.images.build(
            fileobj=dockerfile,
            tag=f"{IMAGE_NAME}:{version}",
            quiet=True,
            buildargs={"CLICKHOUSE_VERSION": version},
        )
    return cast(Image, image)
