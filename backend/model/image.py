from backend.google_apis.sheet import image_link
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from .match import Match

class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: str = Field(primary_key=True)
    name: str = Field()
    bucket_name: str = Field()
    web_entities_requested: Optional[int] = Field(default=None)
    web_entities_found: Optional[int] = Field(default=None)
    show: bool = Field(default=True)
    used_in: Optional[str] = Field(default=None)
    selected_attribution: Optional[int] = Field(foreign_key="matches.id", index=True, nullable=False)
    comment: Optional[str] = Field(default=None)

    # Relationship to matches
    matches: List["Match"] = Relationship(back_populates="parent_image", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    @property
    def gcs_uri(self):
        return f"gs://{self.bucket_name}/{self.name}"

    def add_match(self, match):
        if match.page_url in [m.page_url for m in self.matches]:
            return
        match.add_license()
        self.matches.append(match)

    @property
    def has_license_text(self):
        return any(m.has_license_text for m in self.matches)

    @property
    def has_license_urls(self):
        return any(m.has_license_urls for m in self.matches)

    def match_limit(self, search_config):
        if self.matches:
            print(f"'{self.blob.name}': adding {search_config.result_increment} matches to existing {len(self.matches)}")
        return len(self.matches) + search_config.result_increment

    @property
    def sorted_matches(self):
        return sorted(self.matches, key=lambda m: m.sort_key)

    @property
    def sheet_cell_representation(self):
        return image_link(self.thumbnail_url)


