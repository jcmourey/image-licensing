from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from urllib.parse import unquote

from backend.database.repository import DatabaseRepository
from backend.model.image import Image


class SelectedMatch(BaseModel):
    selected_match_id: int

# Create a separate router for comments to avoid conflicts
router = APIRouter()

@router.put("/api/image/{image_id:path}/selected_match_id", response_model=dict)
def update_selected_match(image_id: str, selected_match: SelectedMatch):
    decoded_image_id = unquote(image_id)

    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Image).where(Image.id == decoded_image_id)
        image = session.exec(statement).first()

        if not image:
            raise HTTPException(status_code=404, detail="selected_match_id: Image not found")

        image.selected_match_id = selected_match.selected_match_id
        session.add(image)

        return {"success": True, "selected_match_id": image.selected_match_id}

