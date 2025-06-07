import requests
import urllib3
from selenium.common import WebDriverException
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column
from typing import Optional, TYPE_CHECKING, Dict, List, Any
from backend.google_apis.sheet import hyperlink
from backend.html_utils.load import load_html
from backend.html_utils.metadata import extract_metadata
from ..licensing.license_types import LICENSES_BY_TYPE

if TYPE_CHECKING:
    from .match import Match

class License(SQLModel, table=True):
    __tablename__ = "licenses"

    id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})
    parent_match_id: int = Field(foreign_key="matches.id", unique=True)
    parent_image_id: str = Field(foreign_key="images.id")
    meta_info: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(MutableDict.as_mutable(JSON)))
    urls: List[str] = Field(default_factory=list, sa_column=Column(MutableList.as_mutable(JSON)))
    error: Optional[str] = None
    approved: bool = Field(default=False)
    preferred_url: Optional[str] = Field(default=None)

    parent_match: Optional["Match"] = Relationship(back_populates="license")

    @classmethod
    def extract_page_license_metadata(cls, match, debug=False):
        try:
            html = load_html(match.page_url)
        except requests.exceptions.HTTPError as err:
            if err.response is not None and err.response.status_code == 404:
                print(f"Error 404: {err}")
                return cls.with_error(match, err)
            else:
                raise err
        except (urllib3.exceptions.NameResolutionError, urllib3.exceptions.ReadTimeoutError, WebDriverException) as err:
            print(err)
            return cls.with_error(match, err)
        except requests.exceptions.ConnectionError as err:
            print(f"Warning: ConnectionError: {err}")
            return None

        meta_info, urls = extract_metadata(html, debug)
        return cls(parent_match_id=match.id, parent_image_id=match.parent_image_id, meta_info=meta_info, urls=urls, error=None)

    @classmethod
    def with_error(cls, match, error):
        return cls(parent_match_id=match.id, parent_image_id=match.parent_image_id, meta_info={}, urls=[],
                   error=str(error))

    @property
    def meta_info_text(self):
        return str(self.meta_info).replace("\\n", "").replace("\\t", "")

    @property
    def is_approved(self):
        return len(self.approved_license_urls) > 0

    @property
    def approved_license_urls(self):
        return [url for url in self.urls if "creativecommons.org" in url or "fandom.com/licensing" in url]

    @property
    def sheet_cell_representation(self):
        first_url = self.urls[0] if self.urls else None
        if first_url:
            return hyperlink(first_url, self.url)
        else:
            return self.meta_info_text or self.error

    @property
    def sort_key(self):
        return (
            not self.is_approved,
            not self.urls,
            not self.meta_info
        )

