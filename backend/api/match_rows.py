from urllib.parse import unquote

from fastapi import APIRouter
from sqlmodel import select

from backend.api.types import MatchRow
from backend.database.repository import DatabaseRepository
from backend.model.match import Match
from backend.model.sort import match_sort_key

router = APIRouter()

@router.get("/api/image/{image_id:path}/match_rows", response_model=list[MatchRow])
async def get_match_rows(image_id: str):
    decoded_image_id = unquote(image_id)
    print(f"Image ID for match_rows: {decoded_image_id}")  # Add this line to print the decoded_image_id)
    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Match).where(Match.parent_image_id == decoded_image_id)
        matches = session.exec(statement).all()
        return make_match_rows(matches)


def make_match_rows(matches: list[Match]):
    matches.sort(key=match_sort_key)
    rank = 1
    rows = []
    for m in matches:
        row = MatchRow.from_match(m, rank)
        rank += 1
        rows.append(row)
    return rows


