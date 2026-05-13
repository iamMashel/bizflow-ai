import base64
import binascii
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Annotated, Any, cast
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    email: str | None = None


def _unauthorized(detail: str = "Invalid or missing authentication token.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode_base64_url(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(f"{value}{padding}")
    except (binascii.Error, ValueError) as exc:
        raise _unauthorized() from exc


def _decode_json_segment(value: str) -> dict[str, Any]:
    try:
        decoded = json.loads(_decode_base64_url(value))
    except json.JSONDecodeError as exc:
        raise _unauthorized() from exc

    if not isinstance(decoded, dict):
        raise _unauthorized()

    return cast(dict[str, Any], decoded)


def verify_supabase_jwt(token: str, jwt_secret: str) -> CurrentUser:
    if not jwt_secret:
        raise _unauthorized("Supabase JWT verification is not configured.")

    parts = token.split(".")
    if len(parts) != 3:
        raise _unauthorized()

    header = _decode_json_segment(parts[0])
    if header.get("alg") != "HS256":
        raise _unauthorized()

    signed_data = f"{parts[0]}.{parts[1]}".encode()
    expected_signature = hmac.new(
        jwt_secret.encode(),
        signed_data,
        hashlib.sha256,
    ).digest()
    actual_signature = _decode_base64_url(parts[2])

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise _unauthorized()

    claims = _decode_json_segment(parts[1])
    expires_at = claims.get("exp")
    if isinstance(expires_at, int | float) and expires_at < time.time():
        raise _unauthorized("Authentication token has expired.")

    subject = claims.get("sub")
    if not isinstance(subject, str):
        raise _unauthorized()

    email = claims.get("email")
    return CurrentUser(
        id=UUID(subject),
        email=email if isinstance(email, str) else None,
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> CurrentUser:
    if credentials is None:
        raise _unauthorized()

    settings = get_settings()
    return verify_supabase_jwt(credentials.credentials, settings.supabase_jwt_secret)
