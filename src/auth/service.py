import uuid
from datetime import datetime, timedelta

from databases.interfaces import Record
from pydantic import UUID4
from sqlalchemy import insert, select
from src import utils
from src.auth.config import auth_config
from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import AuthUser
from src.auth.security import check_password, hash_password
from src.database import auth_user, database, messages, refresh_tokens
from typing import Optional, Union



async def create_user(user: AuthUser) -> Record | None:
    insert_query = (
        insert(auth_user)
        .values(
            {
                "email": user.email,
                "password": hash_password(user.password),
                "created_at": datetime.utcnow(),
            }
        )
        .returning(auth_user)
    )

    return await database.fetch_one(insert_query)

"""
auth_user.c refers to the columns of the auth_user table in the database. It is used in the select queries to specify which columns to retrieve data from.
For example, in the get_user_by_uuid function, select_query = select(auth_user).where(auth_user.c.uuid == user_uuid) specifies that 
we want to select all columns from the auth_user table where the id column matches the user_uuid parameter. The .c attribute is used to access the columns of the table.
"""
async def get_user_by_uuid(user_uuid: int) -> Record | None:
    select_query = select(auth_user).where(auth_user.c.uuid == user_uuid)
    return await database.fetch_one(select_query)


async def get_user_by_email(email: str) -> Record | None:
    print(f"get_user_by_email: {auth_user.c.email}")
    select_query = select(auth_user).where(auth_user.c.email == email)
    return await database.fetch_one(select_query)


"""
The * is used to indicate that all the parameters that follow must be specified using keyword arguments. This means that the user_id parameter must be specified as user_id=<value>
and the refresh_token parameter can be optionally specified as refresh_token=<value>.

For example, to call this function with a user_id of 123 and a refresh_token of "abc", you would write await create_refresh_token(user_id=123, refresh_token="abc"). 
If you omit the refresh_token argument, it will default to None.

Optional[Union[str, None]] is a type hint in Python that indicates that the argument refresh_token is optional and can be either a string or None.
"""
async def create_refresh_token(
    *, user_id: int, refresh_token: Optional[Union[str, None]] = None
) -> str:
    if not refresh_token:
        refresh_token = utils.generate_random_alphanum(64)

    insert_query = refresh_tokens.insert().values(
        uuid=uuid.uuid4(),
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(seconds=auth_config.REFRESH_TOKEN_EXP),
        user_id=user_id,
    )
    await database.execute(insert_query)
    return refresh_token


async def get_refresh_token(refresh_token: str) -> Record | None:
    select_query = refresh_tokens.select().where(
        refresh_tokens.c.refresh_token == refresh_token
    )
    return await database.fetch_one(select_query)


"""
The expire_refresh_token function is used to expire a refresh token by updating its expires_at field in the refresh_tokens table of the database.
The expires_at field is set to the current time minus one day, which effectively makes the refresh token invalid and expired. 
"""
async def expire_refresh_token(refresh_token_uuid: UUID4) -> None:
    update_query = (
        refresh_tokens.update()
        .values(expires_at=datetime.utcnow() - timedelta(days=1))
        .where(refresh_tokens.c.uuid == refresh_token_uuid)
    )
    await database.execute(update_query)


async def authenticate_user(auth_data: AuthUser) -> Record:
    user = await get_user_by_email(auth_data.email)
    #If user is None or False, then the condition is true 
    if not user:
        raise InvalidCredentials()

    if not check_password(auth_data.password, user["password"]):
        raise InvalidCredentials()

    return user


async def send_message(payload: dict[str, str], user_id: int) -> dict[str, str]:
    message = payload["message"]

    insert_query = (
        insert(messages)
        .values(
            message=message,
            user_id=user_id,
        )
        .returning(messages)
    )
    return await database.fetch_one(insert_query)