from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery

from api.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    api_key_header: str = Security(api_key_header),
    api_key_query: str = Security(api_key_query),
) -> str:
    if api_key_header == settings.API_KEY:
        return api_key_header
    if api_key_query == settings.API_KEY:
        return api_key_query

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
