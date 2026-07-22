from sqlalchemy import CheckConstraint, Column, String, Text

from app.core.constants import MAX_PROJECT_NAME_LENGTH
from app.models.base import CharityProjectDonationBaseModel


class CharityProject(CharityProjectDonationBaseModel):
    __table_args__ = (
        CheckConstraint('length(name) > 0', name='name_not_empty'),
        CheckConstraint(
            'length(description) > 0', name='description_not_empty'
        ),
    )

    name = Column(String(MAX_PROJECT_NAME_LENGTH), unique=True, nullable=False)
    description = Column(Text, nullable=False)
