from fastapi import APIRouter, HTTPException
from sqlmodel import select
from urllib.parse import unquote

from backend.api.match_rows import make_match_rows
from backend.api.types import ImageRow
from backend.database.repository import DatabaseRepository
from backend.model.image import Image

router = APIRouter()

@router.post("/api/image/{image_id:path}/hide", response_model=dict)
def hide_image(image_id: str):
    decoded_image_id = unquote(image_id)
    
    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Image).where(Image.id == decoded_image_id)
        image = session.exec(statement).first()

        if not image:
            raise HTTPException(status_code=404, detail="hide: Image not found")

        image.show = False
        session.add(image)

        return {"success": True}


@router.get("/api/image/{image_id:path}/get", response_model=ImageRow)
def get_image_by_id(image_id: str):
    decoded_image_id = unquote(image_id)
    database = DatabaseRepository()
    with database.session_scope() as session:
        image = session.get(Image, decoded_image_id)
        if image is None:
            raise HTTPException(status_code=404, detail="get image: Image not found")
        return image_row_from_image(image, rank=0)


def thumbnail_api(image: Image):
    return f"/api/thumbnail/{image.name}"


def image_row_from_image(image: Image, rank: int):
    ranked_match_rows = make_match_rows(image.matches)
    selected_match = next((m for m in ranked_match_rows if m.id == image.selected_match_id),
                          None) if image.selected_match_id is not None else None
    best_match = next((m for m in ranked_match_rows), None)
    return ImageRow(
        id=image.id,
        number=image.number,
        rank=rank,
        thumbnail_url=thumbnail_api(image),
        selected_match=selected_match,
        best_match=best_match,
        used_in=image.used_in,
        comment=image.comment,
        replacement_page_url=image.replacement_page_url
    )

