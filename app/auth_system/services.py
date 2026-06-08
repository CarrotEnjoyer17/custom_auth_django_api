import uuid
from datetime import datetime, timezone

import jwt
from django.conf import settings


def create_access_token(user_id: int, session_id: uuid.UUID, token_jti: uuid.UUID):
    expires_at = datetime.now(timezone.utc) + settings.JWT_ACCESS_TOKEN_LIFETIME

    payload = {
        "user_id": user_id,
        "session_id": str(session_id),
        "jti": str(token_jti),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )