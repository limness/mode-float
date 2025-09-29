from fastapi import APIRouter, Depends

from backend.middleware import get_current_user
from backend.schemas.user_schema import UserInfoResponseSchema

router = APIRouter(tags=['Users'])


@router.get('/me', response_model=UserInfoResponseSchema)
async def get_me(current_user: dict = Depends(get_current_user)) -> UserInfoResponseSchema:
    return UserInfoResponseSchema(**current_user)
