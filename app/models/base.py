from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer

from app.core.db import Base


class CharityProjectDonationBaseModel(Base):
    __abstract__ = True

    full_amount = Column(
        Integer,
        CheckConstraint('full_amount > 0', name='full_amount_positive'),
        nullable=False,
    )
    invested_amount = Column(
        Integer,
        CheckConstraint(
            'invested_amount >= 0', name='invested_amount_non_negative'
        ),
        CheckConstraint(
            'invested_amount <= full_amount',
            name='invested_amount_not_exceeds_full_amount',
        ),
        default=0,
        nullable=False,
    )
    fully_invested = Column(Boolean, default=False, nullable=False)
    create_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    close_date = Column(DateTime, nullable=True)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(id={self.id}, '
            f'full_amount={self.full_amount}, '
            f'invested_amount={self.invested_amount}, '
            f'fully_invested={self.fully_invested})'
        )
