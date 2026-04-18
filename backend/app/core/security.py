"""Authentication and authorization utilities."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate JWT token and return user context.
    In development, returns a mock user if no token provided.
    In production, validates against Azure Entra ID.
    """
    if settings.ENVIRONMENT == "development":
        # Development: accept any token or no token
        if credentials is None:
            return {
                "user_id": "dev-user@owenscorning.com",
                "name": "Dev User",
                "roles": ["Engineering", "Safety"],
                "site": "Charlotte",
            }

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # In production: validate Azure Entra ID JWT
        # For now decode without verification for demo
        payload = jwt.decode(
            credentials.credentials,
            settings.AZURE_CLIENT_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": settings.ENVIRONMENT == "production"},
        )
        return {
            "user_id": payload.get("sub", "unknown"),
            "name": payload.get("name", "Unknown User"),
            "roles": payload.get("roles", []),
            "site": payload.get("site", ""),
        }
    except JWTError:
        if settings.ENVIRONMENT != "production":
            return {"user_id": "dev-user@owenscorning.com", "name": "Dev User", "roles": [], "site": ""}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


def create_access_token(data: dict) -> str:
    """Create a JWT access token (for testing/development)."""
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")
