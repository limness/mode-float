import logging
from functools import lru_cache
from typing import Dict, Optional

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.settings import keycloak_settings

logger = logging.getLogger(__name__)

security = HTTPBearer()

8d29452edcde:/float-mode# curl http://keycloak:8080/sso/realms/float-mode/protocol/openid-connect/certs
{"keys":[{"kid":"y1QJn0ylLc4b-PjeN57PlNWji6Q5LimTf6ZPNR9Dbn4","kty":"RSA","alg":"RSA-OAEP","use":"enc","n":"2NphCgi50TE3U3GokmaLJYU2mKwq0ZiGH5MEpHeBbACZIn3J9x_cRfRRjD27rln3Hk3emdROhvCM81OuU1PhUfgrmCQaLp5ErjvOYiq6_qTnzdRNZKDRpA1yniaKEr8Fv_81CsPAj9OMo7khuZ0x4vw2FZfvoE4uM63J_HYOFGp2dxOzS3LzT0QodqZccEnuwsPWvwDYqBIaey17Ct16T6Il6CM-mz-801SYkkxa3dwxnhQ01Zhp8FfrztODWQgUiVKelftw","e":"AQAB","x5c":["MIICozCCAYsCBgGZiD88wjANBgkqhkiG9w0BAQsFADAVMRMwyNTYwOVoXDTM1MDkyNjIyNTc0OVowFTETMBEGA1UEAwwKZmxvYXQtbW9kZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANjaYQoIudExN1NxqJJmiyWFNpisKtGYhh+TBKR3r+olrHJ9yfcf3EX0UYw9u65Z9x5N3pnUTobwjPNTrlNT4VH4K5gkGi6eRK47zmIquv6k583UTWSg0aQNcp4mihK/Bb//NQrDwI/TjKO5IbmdMeL8NhWX76BOLjOtyfx2DhRqdncTs0ty809EKHai0veoOsLD1r8A2KgSGnstewrdek+iJegjPps/vNNUmJJMWt3cMZ4UNNWYafBX687Tg1kIFIlSnpX7cCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAjoQ3Ao1zlhcpmuvB+GDSB29Ow1/j02w/5S6xgGYzRoD8quVVKpwhD4UvrC2Yd64Q5P4QlXoHTP1Z6yNQiccJpCCnxKmZ6hCYbrQEdlJle/zHcCzclhveaH9Vm8FgcP5GN6vkA9cqexledA53gMhFYEsJaC0M8k7BWbh51J4KiHh9wqrdDxSV5JzWDWQuCF6lxZYTVZSH5gQu/QwdlIhnZ6UQQtY2a2z4YE+ZnHaVhwmU52e1vkXg9Gw2cGzbw1w0Kk91uy9A=="],"x5t":"hZDQNRNk90DAS0YOwa55pJ7tqSs","x5t#S256":"ts8HBsaiYZ6sXYdanpIoLIKBYUueFMU7tfBu674GOxseFsiqacLP3Mmmoo","kty":"RSA","alg":"RS256","use":"sig","n":"wQSZEVbViLgLQtsL0w9hZmfs8lfrCeqGHV_rY1d6hBROKtld2tRXSqtyEtmQDd270jGwFeMztwq6zgRBJp3DOrfmSmEjZFk-dMheVx6HEN7aNJpaJT8uFT-dwYbugV-1JMQ0hrD8d8N4kC9a5EPKEXK5QvvKwquR_QQUEke9DhVOJmvFXY35wHbQiOPy8XQ1XhtlgXl8HVhxSa7MNZEMXW760WosDpMF6bcqL-h57aYEZnYMddLPJb3FQ9DhsmUUsMa0Fh6Q","e":"AQAB","x5c":["MIICozCCAYsCBgGZiD86eDANBgkqhkiG9w0BAQsFADAVMRMwEQYDVQQDDApmbG9hdC1tb2Rl0OVowFTETMBEGA1UEAwwKZmxvYXQtbW9kZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMEEmRFW1Yi4C0LbC9MPYWZn7PJX6wnqhh1f62NXeoQUTirZXdrUV0qrchLZkA3duxDBPRXjM7cKus4EQSadwzq35kphI2RZPnTIXlcehxDe2jSaWiU/LhU/ncGG7oFftSTENIaw/HfDeJAvWuRDyhFyuUL7ysKrkf0EFBJHvQ4VTiZrxV2N+cB20Ijj8vF0NV4bZYF5fB1YcUmuzDWYOSIgytFqLA6TBem3Ki/oee2mBGZ2DHXSzyW9xUPQ4bJlFLDGtBYekCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAGTnPNIoBzoGH2qElol+LjwbI7Rl1VdZ6frr5yjazsY+wVX5sdYJGifphqHD2+z2OVxvGXaYlV5+6zAVpv6PgzzPkI1jEmm3CgFuepWxwczAg/UoDnDAW7vdp6t1iDKHWgGSXsY09krNeKWmv2wv+MZmB3QNgP3J+b2S+ufgbSWucjBs6ZVRLVwCKEUGUqS67wkqWkfix38kfXI5Qe2QLF



class JWTKeycloakValidator:
    def __init__(self, keycloak_url: str, realm: str):
        self.keycloak_url = keycloak_url
        self.realm = realm
        self.jwks_url = f'{keycloak_url}/sso/realms/{realm}/protocol/openid-connect/certs'

    # @lru_cache(maxsize=1)
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
            print(jwks, '//', kid)
            logger.info('jwt %s /// %s', jwks, kid)

            # Find matching key
            key_data = self.get_key_by_kid(jwks, kid)
            if not key_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Unable to find matching key {kid} for {jwks}'
                )

            # Create public key from JWK
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)

            # Validate token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=keycloak_settings.KEYCLOAK_CLIENT_ID,
                issuer=f'{self.keycloak_url}/sso/realms/{self.realm}',
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
    return {
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


def require_roles(required_roles: list[str]):
    def role_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_roles = current_user['user']['roles'] + current_user['user']['client_roles']

        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f'Required roles: {required_roles}'
            )

        return current_user

    return role_checker


def require_groups(required_groups: list[str]):
    def group_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_groups = current_user['user']['groups']

        if not any(group in user_groups for group in required_groups):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f'Required groups: {required_groups}'
            )

        return current_user

    return group_checker


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths: list[str] | None = None):
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
