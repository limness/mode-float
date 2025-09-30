from datetime import datetime, timezone
from typing import Any

import jwt


def sign_jwt_ps256(
    private_key_pem: str,
    embed_id: str,
    ttl_seconds: int,
    params: dict[str, str | list[str]] | None,
) -> str:
    """Create a short-lived DataLens embed JWT (PS256).

    Payload must include:
      - embedId
      - dlEmbedService (constant marker expected by DataLens)
      - iat, exp

    Args:
        private_key_pem: RSA private key in PEM format.
        embed_id: DataLens embed identifier.
        ttl_seconds: Token lifetime in seconds.
        params: Optional signed params.

    Returns:
        JWT string ready to be placed after #dl_embed_token=
    """
    now = int(datetime.now(tz=timezone.utc).timestamp())
    payload: dict[str, Any] = {
        'embedId': embed_id,
        'dlEmbedService': 'YC_DATALENS_EMBEDDING_SERVICE_MARK',
        'iat': now,
        'exp': now + ttl_seconds,
    }
    if params:
        payload['params'] = params

    return jwt.encode(payload, private_key_pem, algorithm='PS256')


def build_embed_url(base_url: str, token: str) -> str:
    """Compose final iframe URL with token in the URL fragment.

    DataLens expects the JWT in the hash part:
      https://.../embeds/dash#dl_embed_token=<JWT>
    """
    base = base_url.rstrip('/')
    return f'{base}/embeds/dash#dl_embed_token={token}'
