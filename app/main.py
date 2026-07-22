from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from app.api.routers import main_router
from app.core.config import settings
from app.core.init_db import create_first_superuser

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
)

app.include_router(main_router)


@app.on_event('startup')
async def startup():
    try:
        await create_first_superuser()
    except OperationalError as error:
        print(f'Не удалось создать суперпользователя при старте: {error}')
