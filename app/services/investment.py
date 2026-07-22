from datetime import datetime
from typing import List, Union

from app.models.charity_project import CharityProject
from app.models.donation import Donation


def _close_fully_invested(obj: Union[CharityProject, Donation]) -> None:
    obj.fully_invested = True
    obj.close_date = datetime.utcnow()


def invest(
    target: Union[CharityProject, Donation],
    sources: List[Union[CharityProject, Donation]],
) -> List[Union[CharityProject, Donation]]:
    changed = []
    for source in sources:
        if target.fully_invested:
            break

        target_rest = target.full_amount - target.invested_amount
        source_rest = source.full_amount - source.invested_amount
        amount = min(target_rest, source_rest)

        target.invested_amount += amount
        source.invested_amount += amount

        if target.invested_amount == target.full_amount:
            _close_fully_invested(target)
        if source.invested_amount == source.full_amount:
            _close_fully_invested(source)

        changed.append(source)

    return changed
