import re

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import select

from backend.database.repository import DatabaseRepository
from backend.licensing.license_types import LICENSES_BY_TYPE
from backend.model.image import Image
from backend.model.match import Match


class ImageRow(BaseModel):
    """
    Python model for ImageRow that corresponds to the TypeScript interface in the frontend.

    This model is used for serializing/deserializing data between the frontend and backend.
    """
    id: str
    thumbnail_url: str
    used_in: Optional[str]
    best_page_url: Optional[str]
    image_url: Optional[str]
    license_url: Optional[str]
    attribution: Optional[str]
    matching_type: Optional[str]
    comment: Optional[str]

router = APIRouter()

def thumbnail_api(image: Image):
    return f"/api/thumbnail/{image.name}"

@router.get("/api/image_rows", response_model=List[ImageRow])
async def get_image_rows():
    """
    Returns a list of ImageRow objects.
    This endpoint corresponds to the ImageRow type in the frontend.
    
    Returns images that are either:
    1. Shown (Image.shown == True), OR
    2. Have a selected attribution (Image.selected_attribution_id is not None)
    
    Rows are sorted in the following order:
    1. Images with known licenses in the sort order of LICENSES_BY_TYPE keys
    2. Images with unknown licenses
    3. Images with no licenses
    4. Images where the matching_type is "visually similar"
    5. Images with no matches
    """
    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Image).where(Image.show == True)
        images = session.exec(statement).all()
        rows = []
        for image in images:
            sorted_matches = sorted(image.matches, key=match_sort_key)
            best_match = sorted_matches[0] if len(sorted_matches) > 0 else None
            license_url = best_match.license.urls[0] if best_match and best_match.license and len(best_match.license.urls) > 0 else None
            attribution = attribution_explanation(license_url)

            row = ImageRow(
                id=image.id,
                thumbnail_url=thumbnail_api(image),
                used_in=image.used_in,
                best_page_url=best_match.page_url if best_match else "",
                image_url=best_match.image_url if best_match else "",
                license_url=license_url,
                attribution=attribution,
                matching_type=best_match.matching_type if best_match else "",
                comment=image.comment
            )
            rows.append(row)
    
    # Sort rows by the specified priority order
    rows.sort(key=row_sort_key)
    return rows

def row_sort_key(row):
    """
    Sort key function for ImageRow objects with the following priority:
    1. Images with known licenses in the sort order of LICENSES_BY_TYPE keys
    2. Images with unknown licenses
    3. Images with no licenses
    4. Images where the matching_type is "visually similar"
    5. Images with no matches
    
    Returns a tuple where earlier elements have higher precedence in sorting.
    Lower values come first in the sorted result.
    """
    # Check if there's no match (no best_page_url)
    has_no_match = not row.best_page_url
    
    # Check if it's a visually similar match
    is_visually_similar = (row.matching_type or "").lower() == "visually similar"
    
    # Determine license type priority
    license_priority = float("inf")  # Default to lowest priority
    has_license = bool(row.license_url)
    
    if has_license:
        # Check if it's a known license type
        for idx, (license_type, urls) in enumerate(LICENSES_BY_TYPE.items()):
            if row.license_url in urls:
                license_priority = idx
                break
        
        # If not found in LICENSES_BY_TYPE, it's an unknown license
        if license_priority == float("inf"):
            license_priority = len(LICENSES_BY_TYPE)  # Just after known licenses
    else:
        # No license, higher priority number (lower priority)
        license_priority = len(LICENSES_BY_TYPE) + 1
    
    # Return sort tuple: (has_no_match, is_visually_similar, license_priority)
    # Each component is ordered from highest to lowest priority
    return (
        has_no_match,
        is_visually_similar,
        license_priority
    )


def match_sort_key(match):
    # Put "visually similar" at the end
    is_visually_similar = int((match.matching_type or "").lower() == "visually similar")
    # Primary: Priority in LICENSES_BY_TYPE by first license_url
    license_urls = getattr(match.license, "urls", []) if match.license else []
    license_type_priority = float("inf")
    primary_license_url = license_urls[0] if license_urls else ""
    for idx, urls in enumerate(LICENSES_BY_TYPE.values()):
        if primary_license_url in urls:
            license_type_priority = idx
            break
    # Secondary: .gov in page_url
    contains_gov = int(".gov" in (match.page_url or "").lower())
    # Next priorities use the license_url (first)
    contains_license = int(bool(re.search(r"license|licensing", primary_license_url, re.I)))
    contains_terms = int("terms" in primary_license_url.lower())
    contains_stock = int("stock.adobe.com" in primary_license_url.lower() or "vectorstock" in primary_license_url.lower())
    # Sort: lower = higher priority
    return (
        is_visually_similar,
        license_type_priority,
        -contains_gov,
        -contains_license,
        -contains_terms,
        -contains_stock,
        match.page_url or ""
    )

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
    
    

def attribution_explanation(license_url):
    if not license_url:
        return "No license URL"
    for key, url_list in LICENSES_BY_TYPE.items():
        if license_url in url_list:
            return key
    return license_url