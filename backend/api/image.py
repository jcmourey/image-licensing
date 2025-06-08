from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session
from urllib.parse import unquote
from backend.database.repository import DatabaseRepository
from backend.model.image import Image

router = APIRouter()

@router.post("/api/image/{image_id:path}/hide", response_model=dict)
def hide_image(image_id: str):
    """
    Hides an image by setting its show field to false.
    
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

        image.show = False
        session.add(image)

        return {"success": True}
