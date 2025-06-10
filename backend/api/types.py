from typing import Optional
from pydantic import BaseModel

from backend.model.match import Match


class MatchRow(BaseModel):
  id: int
  rank: int
  image_url: str
  page_url: str
  title: str
  matching_type: str
  license_url: Optional[str]
  attribution: Optional[str]
  licensed_by: Optional[str]

  @classmethod
  def from_match(cls, match: Match, rank: int):
    return cls(
        id=match.id,
        rank=rank,
        image_url=match.image_url,
        page_url=match.page_url,
        title=match.title,
        matching_type=match.matching_type,
        license_url=match.preferred_license_url,
        attribution=match.attribution,
        licensed_by=match.licensed_by
    )


class ImageRow(BaseModel):
    """
    Python model for ImageRow that corresponds to the TypeScript interface in the frontend.

    This model is used for serializing/deserializing data between the frontend and backend.
    """
    id: str
    number: int
    rank: int
    thumbnail_url: str
    selected_match: Optional[MatchRow]
    best_match: Optional[MatchRow]
    used_in: Optional[str]
    comment: Optional[str]
    replacement_page_url: Optional[str]
