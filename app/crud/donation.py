from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation
from app.models.user import User
from app.schemas.donation import DonationCreate


class CRUDDonation(CRUDBase[Donation, DonationCreate]):

    async def get_by_user(self, user: User, session: AsyncSession):
        db_donations = await session.execute(
            select(Donation).where(Donation.user_id == user.id)
        )
        return db_donations.scalars().all()

    async def get_open_donations(self, session: AsyncSession):
        db_donations = await session.execute(
            select(Donation)
            .where(Donation.fully_invested.is_(False))
            .order_by(Donation.create_date)
        )
        return db_donations.scalars().all()


donation_crud = CRUDDonation(Donation)
