import requests
import urllib3
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column, select
from typing import Optional, TYPE_CHECKING, Dict, List, Any
from backend.google_apis.sheet import hyperlink
from backend.html_utils.load import load_html
from backend.html_utils.metadata import extract_metadata

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
        except urllib3.exceptions.NameResolutionError as err:
            print(f"NameResolutionError: {err}")
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

    @classmethod
    def fix_license_metadata(cls, database):
        with database.session_scope() as session:
            statement = select(License)
            licenses = session.exec(statement).scalars().all()
            print(f"Fixing metadata in {len(licenses)} licenses")
            changed_licenses = 0
            for license in licenses:
                if license.parent_image_id == 'image-licensing-file/Moving Museum_rollups_printer margin-6.png/1747851738070083':
                    pass
                changed = False
                for key in list(license.meta_info.keys()):
                    value = license.meta_info[key]
                    if isinstance(value, str) and value.startswith("http"):
                        print(f"Found URL: {value}")
                        del license.meta_info[key]
                        license.urls.append(value)
                        changed = True
                if changed:
                    changed_licenses += 1
                    session.add(license)
                    session.commit()
            print(f"Updated {changed_licenses} licenses")

    @property
    def meta_info_text(self):
        return str(self.meta_info).replace("\\n", "").replace("\\t", "")

    @property
    def is_creative_commons_license(self):
        return any("creativecommons.org" in url for url in self.urls)

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
            not self.is_creative_commons_license,
            not self.urls,
            not self.meta_info
        )