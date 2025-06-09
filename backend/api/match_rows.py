from urllib.parse import unquote

from fastapi import APIRouter
from sqlmodel import select

from backend.api.image_rows import match_sort_key
from backend.api.types import MatchRow
from backend.database.repository import DatabaseRepository
from backend.licensing.license_types import attribution_explanation
from backend.model.match import Match
from backend.utilities.url import get_domain_without_suffix

router = APIRouter()

@router.get("/api/image/{image_id:path}/match_rows", response_model=list[MatchRow])
async def get_match_rows(image_id: str):
    decoded_image_id = unquote(image_id)
    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Match).where(Match.parent_image_id == decoded_image_id)
        matches = session.exec(statement).all()
        matches.sort(key=match_sort_key)
        rows = []
        for m in matches:
            license_url = m.license.preferred_url if m.license else None
            row = MatchRow(
                id=m.id,
                image_url=m.image_url,
                page_url=m.page_url,
                title=m.title,
                matching_type=m.matching_type,
                license_url=license_url,
                attribution=attribution_explanation(license_url, m.page_url),
                licensed_by=get_domain_without_suffix(license_url)
            )
            rows.append(row)
    return rows
