from fastapi import FastAPI, Depends, Security
from typing import Annotated
import subprocess
import logging
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from .auth import get_api_key

CLICKHOUSE_VERSION = "23.11.3.23"
app = FastAPI(title="Clickhouse Format Service", version="0.1.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


AUTH_TOKEN = Annotated[str, Depends(oauth2_scheme)]


class User(BaseModel):
    """User model for OAuth2"""

    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    return fake_decode_token(token)


@app.get("/")
async def get_current_docker_info() -> str:
    """Return clickhouse version"""
    return CLICKHOUSE_VERSION


def filter_jemalloc_statement(stderr: str) -> str:
    """https://github.com/ClickHouse/ClickHouse/issues/15611
    This can be printed to stderr when we don't want it to be."""
    lines = stderr.split("\n")
    catch_phrase = "<jemalloc>: Number of CPUs detected"
    return "\n".join([line for line in lines if catch_phrase not in line])


async def run_clickhouse_format(sql: str) -> str:
    """Take a SQL string and run it through clickhouse format invoked via subprocess
    clickhouse format --quiet --multiquery --query `sql`. However, we make it safe
    against injection and follow best practices for subprocess invocations."""

    try:
        completed_process = subprocess.run(
            ["clickhouse", "format", "--quiet", "--multiquery"],
            input=sql,
            capture_output=True,
            text=True,
            check=True,
        )
        output = filter_jemalloc_statement(completed_process.stderr)
    except subprocess.CalledProcessError as e:
        if not e.stderr:
            raise e

        output = filter_jemalloc_statement(e.stderr)

    for line in output.split("\n"):
        logging.getLogger("uvicorn.error").info(f"{line}")

    return output


@app.post("/")
async def clickhouse_format_sql(sql: str, api_key: str = Security(get_api_key)) -> str:
    """Get the first image matching the name or build the image if it does not exist,
    then run the container for that image feeding the input in and returning the container
    output"""
    logging.getLogger("uvicorn.error").info(f"{api_key=}")
    logging.getLogger("uvicorn.error").debug(f"received SQL: {sql}")

    return await run_clickhouse_format(sql)
