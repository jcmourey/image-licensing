from typing import Optional, TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship
from .license import License
from .sort import attribution_explanation
from ..utilities.url import get_domain_without_suffix

if TYPE_CHECKING:
    from .image import Image

class Match(SQLModel, table=True):
    __tablename__ = "matches"

    id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})
    parent_image_id: str = Field(foreign_key="images.id", index=True, nullable=False)
    page_url: str = Field()
    title: str = Field()
    image_url: str = Field()
    matching_type: str = Field()
    license: Optional[License] = Relationship(
        back_populates="parent_match",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )
    parent_image: "Image" = Relationship(
        back_populates="matches",
        sa_relationship_kwargs={"foreign_keys": "[Match.parent_image_id]"}
    )
    __table_args__ = (
        UniqueConstraint("parent_image_id", "page_url", name="uix_parent_image_image_url"),
    )

    @property
    def preferred_license_url(self):
        return self.license.preferred_url if self.license else None

    @property
    def attribution(self):
        return attribution_explanation(self.preferred_license_url, self.page_url)

    @property
    def licensed_by(self):
        return get_domain_without_suffix(self.preferred_license_url)