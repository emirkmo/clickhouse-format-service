import os
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyQuery

API_KEY_QUERY = APIKeyQuery(
    name="api_key",
    auto_error=False,
    description="ENTER YOUR API KEY",
    scheme_name="API KEY",
)


async def get_api_key(
    api_key: str = Security(API_KEY_QUERY),
) -> str:
    """
    Get api key from `api_key` header or query parameter, authenticate on match to secret.

    :param api_key_header: api_key header.
    :param api_key_query: api_key in query.
    :return: string api_key.

    Raises
    :raise: HTTPException
    """
    if api_key == os.getenv("API_KEY"):
        return api_key

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate API KEY.",
    )
