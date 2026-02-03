from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.config import API_KEY

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: Optional[str] = Depends(_api_key_header)) -> None:
    if key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
