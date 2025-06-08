from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from urllib.parse import unquote

from backend.database.repository import DatabaseRepository
from backend.model.image import Image


class CommentUpdate(BaseModel):
    comment: str

# Create a separate router for comments to avoid conflicts
router = APIRouter()

@router.put("/api/image/{image_id:path}/comment", response_model=dict)
def update_image_comment(image_id: str, comment_data: CommentUpdate):
    """
    Updates the comment for an image.
    
    The image_id parameter may contain slashes and will be URL-encoded by the client.
    We use the :path converter to properly handle slashes in the URL path.
    """
    # Explicitly decode the URL-encoded image_id to handle slashes correctly
    decoded_image_id = unquote(image_id)
    
    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Image).where(Image.id == decoded_image_id)
        image = session.exec(statement).first()

        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        new_comment = comment_data.comment
        image.comment = new_comment if new_comment.strip() != "" else None
        session.add(image)
        session.commit()

        return {"success": True, "comment": comment_data.comment}

