from datetime import datetime, timedelta

from databases.interfaces import Record
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.auth.config import auth_config
from src.auth.exceptions import AuthorizationFailed, AuthRequired, InvalidToken
from src.auth.schemas import JWTData

# The tokenUrl parameter specifies the URL where the client can obtain a token. 
# The auto_error parameter is set to False, which means that if the token is not present in the request, 
# the OAuth2PasswordBearer instance will return None instead of raising an exception.
# This instance is used as a dependency in the parse_jwt_user_data_optional function, which is used to parse the JWT token and 
# return its payload as a JWTData object.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/tokens", auto_error=False)

#sub = subject
def create_access_token(
    *,
    user: Record,
    expires_delta: timedelta = timedelta(minutes=auth_config.JWT_EXP),
) -> str:
    jwt_data = {
        "sub": str(user["uuid"]),
        "exp": datetime.utcnow() + expires_delta,
        "is_admin": user["is_admin"],
    }

    return jwt.encode(jwt_data, auth_config.JWT_SECRET, algorithm=auth_config.JWT_ALG)


async def parse_jwt_user_data_optional(
    token: str = Depends(oauth2_scheme),
) -> JWTData | None:
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, auth_config.JWT_SECRET, algorithms=[auth_config.JWT_ALG]
        )
    except JWTError:
        raise InvalidToken()

    return JWTData(**payload)


async def parse_jwt_user_data(
    token: JWTData | None = Depends(parse_jwt_user_data_optional),
) -> JWTData:
    if not token:
        raise AuthRequired()

    return token


async def parse_jwt_admin_data(
    token: JWTData = Depends(parse_jwt_user_data),
) -> JWTData:
    if not token.is_admin:
        raise AuthorizationFailed()

    return token


async def validate_admin_access(
    token: JWTData | None = Depends(parse_jwt_user_data_optional),
) -> None:
    if token and token.is_admin:
        return

    raise AuthorizationFailed()
