from base64 import b64decode
from typing import Union
from datetime import datetime, timedelta
import jwt
from dependency_injector.wiring import inject
from fastapi import Request, HTTPException
from jwt import ExpiredSignatureError, DecodeError
from starlette.status import HTTP_403_FORBIDDEN
from config.settings import SECRET_KEY
from src.base.base import JwtHTTPBearer
from src.users.models import User


class UserAuth(JwtHTTPBearer):

    def __init__(self):
        super().__init__()

    @inject
    async def __call__(
            self,
            request: Request
    ) -> Union[User, None]:
        bearer = await super().__call__(request)
        if token_verify(bearer.credentials):
            return bearer
        else:
            return None


def token_verify(access_token: str):
    try:
        header_data = jwt.get_unverified_header(access_token)
        try:
            jwt.decode(
                access_token,
                key=SECRET_KEY,
                leeway=10,
                algorithms=["HS256"]
            )
            return access_token

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Token expired"
            )
    except DecodeError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Token invalid"
        )


def create_access_token(user_id: int, remember_me: bool) -> str:
    iat = datetime.utcnow()
    expiration_time = datetime.utcnow() + timedelta(seconds=15)

    if remember_me:
        # token data
        payload = {
            'user_id': user_id,
            'iat': iat,
            "type": 'Bearer',
        }
    else:
        # token data
        payload = {
            'user_id': user_id,
            'iat': iat,
            'exp': expiration_time,
            "type": 'Bearer',
        }

    access_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(f'Create token - {access_token}')
    return payload.get('type') + ' ' + access_token


def decode_token(access_token: str) -> dict:
    try:
        header_data = jwt.get_unverified_header(access_token)
        print('Decode token - ', access_token)
        payload = jwt.decode(
            access_token,
            key=SECRET_KEY,
            leeway=10,
            algorithms=["HS256"]
        )

        print('Decode token payload - ', payload)
        return payload
    except Exception as error:
        print(error)
        return error
