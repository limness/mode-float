from fastapi import (
    APIRouter,
    status,
)

from backend.core.settings import datalens_settings
from backend.exc import IDException
from backend.schemas.dashboard_schema import DatalensEmbedRequestSchema, DatalensEmbedResponseSchema
from backend.services.dashboard_service import build_embed_url, sign_jwt_ps256

router = APIRouter(tags=['Dashboards'])


@router.post(
    '/embed/datalens',
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_groups(['administrators']))],  # optional ACL
)
async def create_datalens_embed_url(
    body: DatalensEmbedRequestSchema,
) -> DatalensEmbedResponseSchema:
    """Выдать короткоживущую безопасную ссылку для встраивания DataLens.

    Примечания по безопасности:
      * Приватный ключ хранится только на бэкенде (Vault/Lockbox/KMS/секреты K8s).
      * Используйте короткий TTL (2–10 минут), когда это возможно.
      * Проверяйте права вызывающей стороны на запрошенный `embed_id`.
    """
    ttl = body.ttl_seconds or datalens_settings.DEFAULT_TTL_SECONDS
    if ttl < datalens_settings.MIN_TTL_SECONDS or ttl > datalens_settings.MAX_TTL_SECONDS:
        raise IDException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f'ttl_seconds must be between {datalens_settings.MIN_TTL_SECONDS} and '
                f'{datalens_settings.MAX_TTL_SECONDS} seconds.'
            ),
        )
    try:
        token = sign_jwt_ps256(
            private_key_pem=datalens_settings.get_datalens_private_key(),
            embed_id=body.embed_id,
            ttl_seconds=ttl,
            params=body.params,
        )
    except Exception as e:  # pragma: no cover
        raise IDException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to sign DataLens JWT: {e}',
        )

    return DatalensEmbedResponseSchema(
        url=build_embed_url(datalens_settings.DATALENS_BASE_URL, token)
    )
