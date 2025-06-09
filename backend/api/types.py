from typing import Optional
from pydantic import BaseModel


class ImageRow(BaseModel):
    """
    Python model for ImageRow that corresponds to the TypeScript interface in the frontend.

    This model is used for serializing/deserializing data between the frontend and backend.
    """
    id: str
    best_match_number: int
    thumbnail_url: str
    used_in: Optional[str]
    best_page_url: str
    image_url: str
    license_url: Optional[str]
    attribution: Optional[str]
    licensed_by: Optional[str]
    matching_type: str
    comment: Optional[str]
    replacement_page_url: Optional[str]
    selected_match_id: int


class MatchRow(BaseModel):
  id: int
  image_url: str
  page_url: str
  title: str
  matching_type: str
  license_url: Optional[str]
  attribution: Optional[str]
  licensed_by: Optional[str]
