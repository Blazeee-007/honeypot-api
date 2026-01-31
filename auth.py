from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from config import settings

API_KEY_NAME = "X-API-KEY"
API_KEY = settings.HONEYPOT_API_KEY

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(
    header_api_key: str = Security(api_key_header),
):
    # Debug print to help identify auth issues
    print(f"DEBUG: Received Key: '{header_api_key}', Expected Key: '{API_KEY}'")
    
    if not header_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-KEY header",
        )
    if header_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key provided",
        )
    return header_api_key
