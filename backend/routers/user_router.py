from fastapi import APIRouter, Depends

from backend.middleware import get_current_user
from backend.schemas.user_schema import UserInfoResponseSchema

router = APIRouter(tags=['Users'])


@router.get('/me', response_model=UserInfoResponseSchema)
async def get_me(current_user: dict = Depends(get_current_user)) -> UserInfoResponseSchema:
    """Вернуть информацию о текущем аутентифицированном пользователе.

    Данные берутся из контекста авторизации и приводятся к схеме ответа.

    - 200: информация успешно возвращена
    - 401: пользователь не аутентифицирован
    """
    return UserInfoResponseSchema(**current_user)
