import secrets

from fastapi import Depends, Header, HTTPException

from app.core.config import Settings, get_settings


def verify_internal_token(
    x_internal_token: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    expected = settings.internal_service_token
    if not x_internal_token or not secrets.compare_digest(
        x_internal_token, expected
    ):
        raise HTTPException(status_code=403, detail="Invalid internal token")
