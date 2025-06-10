
from fastapi import APIRouter, HTTPException
from typing import List

from sqlmodel import select

from backend.api.image import image_row_from_image
from backend.api.types import ImageRow
from backend.database.repository import DatabaseRepository
from backend.model.image import Image
from backend.model.sort import row_sort_key

router = APIRouter()

@router.get("/api/image_rows", response_model=List[ImageRow])
async def get_image_rows():
    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Image).where(Image.show == True)
        images = session.exec(statement).all()
        rows = []
        rank = 1
        for image in images:
            row = image_row_from_image(image, rank)
            rows.append(row)
            rank += 1
    
        # Sort rows by the specified priority order
        rows.sort(key=row_sort_key)
        return rows


@router.put("/api/image/{image_id}/used_in", response_model=dict)
async def update_image_used_in(image_id: str, data: dict):
    """
    Updates the used_in field for an image.

    Args:
        image_id: The ID of the image to update
        data: JSON body containing the 'used_in' field

    Returns:
        A dictionary with the updated image ID and status
    """
    if 'used_in' not in data:
        raise HTTPException(status_code=400, detail="Missing 'used_in' field in request body")
    
    used_in = data['used_in']
    
    database = DatabaseRepository()
    try:
        with database.session_scope() as session:
            # Find the image by ID
            image = session.exec(select(Image).where(Image.id == image_id)).first()
            if not image:
                raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found")
            
            # Update the used_in field
            image.used_in = used_in
            session.add(image)
            
        return {"id": image_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update used_in: {str(e)}")
    

