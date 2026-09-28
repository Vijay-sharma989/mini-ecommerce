from datetime import datetime, timedelta, timezone

import jwt

from app.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire
    })

    token = jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        JWT_ALGORITHM
    )

    return token