from typing import Optional
from dependency_injector.wiring import inject
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_403_FORBIDDEN


class JwtHTTPBearer(HTTPBearer):

    async def __call__(
            self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:

        if request.cookies.get("access_token"):
            authorization = request.cookies.get("access_token")
            scheme, credentials = get_authorization_scheme_param(authorization)
        else:
            authorization = request.headers.get('authorization')
            scheme, credentials = get_authorization_scheme_param(authorization)

        if credentials == 'bearer':
            return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)

        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None

        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
