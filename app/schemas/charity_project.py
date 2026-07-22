from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from app.core.constants import (
    MAX_PROJECT_NAME_LENGTH,
    MIN_PROJECT_DESCRIPTION_LENGTH,
    MIN_PROJECT_NAME_LENGTH,
)


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=MIN_PROJECT_NAME_LENGTH,
        max_length=MAX_PROJECT_NAME_LENGTH,
    )
    description: Optional[str] = Field(
        None, min_length=MIN_PROJECT_DESCRIPTION_LENGTH
    )
    full_amount: Optional[PositiveInt] = None

    model_config = ConfigDict(extra='forbid')


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(
        ...,
        min_length=MIN_PROJECT_NAME_LENGTH,
        max_length=MAX_PROJECT_NAME_LENGTH,
    )
    description: str = Field(
        ..., min_length=MIN_PROJECT_DESCRIPTION_LENGTH
    )
    full_amount: PositiveInt


class CharityProjectUpdate(CharityProjectBase):
    pass


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
