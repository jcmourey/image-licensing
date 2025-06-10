from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from urllib.parse import unquote

from backend.database.repository import DatabaseRepository
from backend.model.image import Image


class CommentUpdate(BaseModel):
    comment: str | None

# Create a separate router for comments to avoid conflicts
router = APIRouter()

@router.put("/api/image/{image_id:path}/comment", response_model=dict)
def update_image_comment(image_id: str, comment_data: CommentUpdate):
    decoded_image_id = unquote(image_id)
    
    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Image).where(Image.id == decoded_image_id)
        image = session.exec(statement).first()

        if not image:
            raise HTTPException(status_code=404, detail="comment: Image not found")

        new_comment = comment_data.comment
        image.comment = new_comment if new_comment and new_comment.strip() != "" else None
        session.add(image)

        return {"success": True, "comment": comment_data.comment}

