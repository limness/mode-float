from src.routers.edit_profile_router import router as edit_profile_router
from src.routers.event_creation_router import router as event_creation_router
from src.routers.event_menu_router import router as event_menu_router
from src.routers.event_request_router import router as event_request_router
from src.routers.matching_router import router as matching_router
from src.routers.profile_router import router as profile_router
from src.routers.reg_router import router as reg_router

__all__ = [
    'event_creation_router',
    'event_request_router',
    'event_menu_router',
    'matching_router',
    'profile_router',
    'reg_router',
    'edit_profile_router',
]
