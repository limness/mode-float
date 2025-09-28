from typing import Literal
from uuid import uuid1

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_database
from src.core.dependencies import ScopeChecker
from src.core.scopes import is_authorized, is_owner, is_owner_or_admin
from src.exc import IDException
from src.schemas.user_schema import CreateUserSchema
from src.services.user_service import UserService, UserTokenService
from src.utils.email_utils import (
    send_password_refresh_on_email,
    send_primary_email_refresh_on_email,
    send_recovery_email_refresh_on_email,
)
from src.utils.enum_utils import TokenConfirmsEnum

app = APIRouter(tags=['Users'])


@app.get('/session', status_code=status.HTTP_200_OK)
async def get_user_session_status(
    session: dict = Depends(ScopeChecker([is_authorized])),
    db_session: AsyncSession = Depends(get_database),
) -> CreateUserSchema:
    if (user := await UserService(db_session).get_user(uid=session['user']['uid'])) is None:
        raise IDException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found!')
    return CreateUserSchema(**user)


@app.get('/{user_id}', dependencies=[Depends(ScopeChecker([is_owner_or_admin]))])
async def get_user(
    user_id: str,
    db_session: AsyncSession = Depends(get_database),
) -> CreateUserSchema:
    if (user := await UserService(db_session).get_user(uid=user_id)) is None:
        raise IDException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found!')

    return CreateUserSchema(**user)


@app.post(
    '/{user_id}/verify-token',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(ScopeChecker([is_owner]))],
)
async def create_verify_token(
    user_id: str,
    background_tasks: BackgroundTasks,
    confirm: Literal[TokenConfirmsEnum.values()] = Query(...),
    db_session: AsyncSession = Depends(get_database),
):
    if (user := await UserService(db_session).get_user(uid=user_id)) is None:
        raise IDException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found!')

    verify_token = str(uuid1())
    token_id = user_id + '-' + confirm
    await UserTokenService().create_verify_token(token_id=token_id, token=verify_token)

    if confirm == TokenConfirmsEnum.PASSWORD_CONFIRM.value:
        background_tasks.add_task(
            send_password_refresh_on_email, token=verify_token, to=user['email']
        )
    elif confirm == TokenConfirmsEnum.RECOVERY_EMAIL_CONFIRM.value:
        background_tasks.add_task(
            send_recovery_email_refresh_on_email, token=verify_token, to=user['email']
        )
    elif confirm == TokenConfirmsEnum.PRIMARY_EMAIL_CONFIRM.value:
        background_tasks.add_task(
            send_primary_email_refresh_on_email, token=verify_token, to=user['email']
        )
    return {}
