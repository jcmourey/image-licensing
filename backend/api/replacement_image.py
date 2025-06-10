from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from urllib.parse import unquote

from backend.database.repository import DatabaseRepository
from backend.model.image import Image


class ReplacementImageUpdate(BaseModel):
    replacement_page_url: str | None


# Create a separate router for comments to avoid conflicts
router = APIRouter()


@router.put("/api/image/{image_id:path}/replacement_page_url", response_model=dict)
def update_replacement_image(image_id: str, replacement_image_data: ReplacementImageUpdate):
    decoded_image_id = unquote(image_id)

    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Image).where(Image.id == decoded_image_id)
        image = session.exec(statement).first()

        if not image:
            raise HTTPException(status_code=404, detail="replacement_page_url: Image not found")

        image.replacement_page_url = replacement_image_data.replacement_page_url
        session.add(image)

        return {"success": True, "replacement_page_url": image.replacement_page_url}

