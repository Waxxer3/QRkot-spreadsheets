from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject
from app.schemas.charity_project import CharityProjectCreate


class CRUDCharityProject(CRUDBase[CharityProject, CharityProjectCreate]):

    async def get_project_id_by_name(
        self, project_name: str, session: AsyncSession
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_project_id.scalars().first()

    async def get_open_projects(self, session: AsyncSession):
        db_projects = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(False))
            .order_by(CharityProject.create_date)
        )
        return db_projects.scalars().all()

    async def get_projects_by_completion_rate(
        self, session: AsyncSession
    ) -> List[CharityProject]:

        db_projects = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(True))
        )
        projects = db_projects.scalars().all()
        return sorted(
            projects,
            key=lambda project: project.close_date - project.create_date,
        )

    async def update(
        self,
        db_obj: CharityProject,
        obj_in,
        session: AsyncSession,
    ) -> CharityProject:
        charity_project = await super().update(db_obj, obj_in, session)
        if (
            not charity_project.fully_invested
            and charity_project.invested_amount
            == charity_project.full_amount
        ):
            charity_project.fully_invested = True
            charity_project.close_date = datetime.utcnow()
            await self.commit_and_refresh(session, charity_project)
        return charity_project


charity_project_crud = CRUDCharityProject(CharityProject)
