import logging
from functools import lru_cache
from typing import Dict, List, Optional

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.settings import keycloak_settings

logger = logging.getLogger(__name__)

security = HTTPBearer()


class JWTKeycloakValidator:
    def __init__(self, keycloak_url: str, realm: str):
        self.keycloak_url = keycloak_url
        self.realm = realm
        self.jwks_url = f'{keycloak_url}/realms/{realm}/protocol/openid_connect/certs'

    @lru_cache(maxsize=1)
    async def get_jwks(self) -> Dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_url, timeout=10.0)
                response.raise_for_status()

                logger.info('JWKS keys fetched from Keycloak')
                return response.json()

        except Exception as e:
            logger.error(f'Failed to fetch JWKS: {e}')
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Unable to validate tokens - Keycloak unavailable',
            )

    def get_key_by_kid(self, jwks: Dict, kid: str) -> Optional[Dict]:
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                return key
        return None

    async def validate_token(self, token: str) -> Dict:
        try:
            # Decode header to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')

            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail='Token missing kid'
                )

            # Get JWKS keys
            jwks = await self.get_jwks()

            # Find matching key
            key_data = self.get_key_by_kid(jwks, kid)
            if not key_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail='Unable to find matching key'
                )

            # Create public key from JWK
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)

            # Validate token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=keycloak_settings.KEYCLOAK_CLIENT_ID,
                issuer=f'{self.keycloak_url}/realms/{self.realm}',
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Token has expired'
            )
        except jwt.InvalidAudienceError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token audience'
            )
        except jwt.InvalidIssuerError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token issuer'
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Invalid token: {str(e)}'
            )
        except Exception as e:
            logger.error(f'Token validation error: {e}')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Token validation failed'
            )


validator = JWTKeycloakValidator(keycloak_settings.KEYCLOAK_URL, keycloak_settings.KEYCLOAK_REALM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authorization header required'
        )

    token = credentials.credentials
    payload = await validator.validate_token(token)

    # Extract user information
    user_info = {
        'uid': payload.get('sub'),
        'username': payload.get('preferred_username'),
        'email': payload.get('email'),
        'first_name': payload.get('given_name'),
        'last_name': payload.get('family_name'),
        'roles': payload.get('realm_access', {}).get('roles', []),
        'client_roles': payload.get('resource_access', {})
        .get(keycloak_settings.KEYCLOAK_CLIENT_ID, {})
        .get('roles', []),
        'groups': payload.get('groups', []),
        'exp': payload.get('exp'),
        'iat': payload.get('iat'),
    }

    return {'user': user_info}


async def get_optional_user(request: Request) -> Optional[Dict]:
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]

    try:
        payload = await validator.validate_token(token)
        user_info = {
            'uid': payload.get('sub'),
            'username': payload.get('preferred_username'),
            'email': payload.get('email'),
            'first_name': payload.get('given_name'),
            'last_name': payload.get('family_name'),
            'roles': payload.get('realm_access', {}).get('roles', []),
            'client_roles': payload.get('resource_access', {})
            .get(keycloak_settings.KEYCLOAK_CLIENT_ID, {})
            .get('roles', []),
            'groups': payload.get('groups', []),
        }
        return {'user': user_info}
    except Exception:
        return None


def require_roles(required_roles: List[str]):
    def role_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_roles = current_user['user']['roles'] + current_user['user']['client_roles']

        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f'Required roles: {required_roles}'
            )

        return current_user

    return role_checker


def require_groups(required_groups: List[str]):
    def group_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_groups = current_user['user']['groups']

        if not any(group in user_groups for group in required_groups):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f'Required groups: {required_groups}'
            )

        return current_user

    return group_checker


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths: List[str] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ['/docs', '/openapi.json', '/health']

    async def dispatch(self, request: Request, call_next):
        # Skip certain paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Check token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                content='{"detail": "Authorization header required"}',
                status_code=401,
                media_type='application/json',
            )

        token = auth_header.split(' ')[1]

        try:
            payload = await validator.validate_token(token)
            request.state.user = payload
        except HTTPException as e:
            return Response(
                content=f'{{"detail": "{e.detail}"}}',
                status_code=e.status_code,
                media_type='application/json',
            )

        return await call_next(request)
