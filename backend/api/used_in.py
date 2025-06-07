from urllib.parse import unquote

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select, col
import base64
from typing import List

from backend.model.image import Image
from backend.database.repository import DatabaseRepository

router = APIRouter()

class UsedInData(BaseModel):
    used_in: str

# Add debug logging for the update endpoint
@router.put("/api/image/{image_id}/used_in")
async def update_image_used_in(image_id: str, data: UsedInData):
    """
    Update the used_in field for a specific image.
    """
    print(f"[DEBUG] Received update request for image {image_id}")
    print(f"[DEBUG] used_in value: '{data.used_in}' (type: {type(data.used_in)})")
    
    # Process the update as normal...
    database = DatabaseRepository()
    with database.session_scope() as session:
        # Find the image by ID
        image = session.exec(select(Image).where(Image.id == image_id)).first()
        if not image:
            print(f"[DEBUG] Image {image_id} not found")
            raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
            
        # Update the used_in field
        print(f"[DEBUG] Updating image used_in from '{image.used_in}' to '{data.used_in}'")
        image.used_in = data.used_in
        session.add(image)
        
    print(f"[DEBUG] Successfully updated used_in for image {image_id}")
    return {"status": "success", "message": "Used in information updated successfully"}

@router.put("/api/image/{image_id:path}/used_in")
async def update_used_in(image_id: str, used_in_data: UsedInData):
    decoded_image_id = unquote(image_id)

    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Image).where(Image.id == decoded_image_id)
        image = session.exec(statement).first()

        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        image.used_in = used_in_data.used_in
        session.add(image)

        return {"success": True, "used_in": used_in_data.used_in}

@router.get("/api/used_in_options", response_model=List[str])
async def get_used_in_options():
    """
    Returns a list of unique used_in values from all Image records in the database.
    """
    database = DatabaseRepository()
    with database.session_scope() as session:
        # Get distinct used_in values that are not null
        statement = select(Image.used_in).where(Image.used_in != None).distinct()
        results = session.exec(statement).all()
        
        # Filter out None values and sort
        options = [used_in for used_in in results if used_in]
        return sorted(options)
