import re

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import select

from backend.database.repository import DatabaseRepository
from backend.licensing.license_types import LICENSES_BY_TYPE, attribution_explanation, contains_gov, contains_canva, \
    contains_org
from backend.model.image import Image
from backend.utilities.url import get_domain_without_suffix


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
    licensed_by: Optional[str]
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
            best_page_url = best_match.page_url if best_match else ""
            attribution = attribution_explanation(license_url, best_page_url)
            licensed_by = get_domain_without_suffix(license_url)

            row = ImageRow(
                id=image.id,
                thumbnail_url=thumbnail_api(image),
                used_in=image.used_in,
                best_page_url=best_page_url,
                image_url=best_match.image_url if best_match else "",
                license_url=license_url,
                attribution=attribution,
                licensed_by=licensed_by,
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
    has_a_match = int(row.best_page_url is not None)
    license_url = row.license_url if row.license_url is not None else ""

    return (
        -has_a_match,
        sort_key(row.best_page_url, row.image_url, license_url, row.matching_type),
    )


def match_sort_key(match):
    license_urls = getattr(match.license, "urls", []) if match.license else []
    primary_license_url = license_urls[0] if license_urls else ""
    return sort_key(match.page_url, match.image_url, primary_license_url, match.matching_type)


def sort_key(page_url, image_url, license_url, matching_type):
    # Put "visually similar" at the end
    not_just_visually_similar = int((matching_type or "").lower() != "visually similar")
    # if there is no page_url
    has_a_page_url = int(page_url != image_url)
    # Primary: Priority in LICENSES_BY_TYPE by first license_url

    license_priority = float("inf")
    for idx, urls in enumerate(LICENSES_BY_TYPE.values()):
        if license_url in urls:
            license_priority = idx
            break
    # Secondary: .gov in page_url
    # More accurately detect government domains by checking for .gov followed by /, ., or end of string
    contains_gov_criteria = int(contains_gov(page_url))
    contains_canva_criteria = int(contains_canva(page_url))
    contains_org_criteria = int(contains_org(page_url))
    # Next priorities use the license_url (first)
    contains_license = int(bool(re.search(r"license|licensing", license_url, re.I)))
    contains_terms = int("terms" in license_url.lower() and license_url != "/terms")
    contains_stock = int(
        "stock.adobe.com" in license_url.lower() or "vectorstock" in license_url.lower())
    # Sort: lower = higher priority
    return (
        -not_just_visually_similar,
        -has_a_page_url,
        license_priority,
        -contains_canva_criteria,
        -contains_license,
        -contains_terms,
        -contains_gov_criteria,
        -contains_org_criteria,
        -contains_stock,
        page_url or ""
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
    

