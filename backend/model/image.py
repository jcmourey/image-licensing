from backend.google_apis.sheet import image_link
from typing import List
from sqlmodel import SQLModel, Field, Relationship
from .match import Match

class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: str = Field(primary_key=True)
    name: str = Field()
    bucket_name: str = Field()

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
    def has_creative_commons_license(self):
        return any(m.license.is_creative_commons_license for m in self.matches)

    @property
    def has_enough(self):
        return self.has_creative_commons_license

    @property
    def has_license_text(self):
        return any(m.has_license_text for m in self.matches)

    @property
    def has_license_urls(self):
        return any(m.has_license_urls for m in self.matches)

    def is_eligible_to_get_more_matches(self, search_config):
        return ((not self.has_license_text and len(self.matches) < search_config.max_results_for_text) or
                (not self.has_license_urls and len(self.matches) < search_config.max_results_for_url) or
                (not self.has_creative_commons_license and len(self.matches) < search_config.max_results_for_creative_commons))

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


