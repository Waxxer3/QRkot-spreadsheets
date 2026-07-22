import logging
from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
    exceptions,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from app.core.config import settings
from app.core.constants import JWT_LIFETIME_SECONDS, MIN_PASSWORD_LENGTH
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


async def get_user_db(session=Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.secret, lifetime_seconds=JWT_LIFETIME_SECONDS
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def validate_password(
        self, password: str, user: Union[UserCreate, User]
    ) -> None:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise exceptions.InvalidPasswordException(
                reason=(
                    f'Пароль должен быть не менее '
                    f'{MIN_PASSWORD_LENGTH} символов.'
                )
            )

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        logger.info('Пользователь %s зарегистрирован.', user.email)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
