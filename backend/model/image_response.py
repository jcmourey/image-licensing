from typing import List
from pydantic import BaseModel

class ImageResponse(BaseModel):
    id: str
    name: str
    thumbnail_url: str
    match_count: int
    license_count: int
    license_urls: List[str]
    has_creative_commons_license: bool
