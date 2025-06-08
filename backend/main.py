from typing import List

from sqlalchemy import func
from sqlmodel import select
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from backend.api.image_rows import get_image_rows
from backend.google_apis.storage import Storage
from backend.image_utils.thumbnail import ThumbnailService
from backend.licensing.license_types import LICENSES_BY_TYPE, known_license_urls
from backend.licensing.style_sheet import style_sheet
from backend.google_apis.sheet_from_db import GoogleSheetFromDatabase
from backend.config.config import Configuration
from backend.model.image import Image
from backend.model.license import License
from backend.model.match import Match
from backend.update.matches import update_images
from backend.update.sync_images import sync_images
from backend.update.thumbnails import update_thumbnails
from backend.update.licenses import update_licenses, fix_unique_licenses, sort_license_urls
from backend.database.repository import DatabaseRepository
from backend.api import image_rows, comment, used_in, image
import tldextract

from backend.utilities.url import get_domain

app = FastAPI(title="Image Management API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(image_rows.router)
app.include_router(image.router)
app.include_router(comment.router)
app.include_router(used_in.router)

@app.get("/")
async def root():
    return {"message": "Image Management API is running"}
# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)

# Example route
@app.get("/api/health")
def health_check():
    print("Health check")
    return {"status": "ok"}


@app.get("/api/root_domains")
def root_domains():
    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Match.page_url).where(Match.page_url is not None).distinct()
        urls = session.exec(statement).all()
        return set(get_domain(url) for url in urls)

@app.get("/api/licenses", response_model=List[str])
def get_distinct_licenses():
    """
    Returns a list of distinct license URLs from all License records in the database.
    """
    database = DatabaseRepository()
    with database.session_scope() as session:
        # Get all License rows
        statement = select(License.urls).where(func.json_array_length(License.urls) > 0)
        results = session.exec(statement).all()
        # results is a list of lists
        all_urls = set()
        for urls in results:
            all_urls.update(urls)
        return list(all_urls)

@app.get("/api/unlisted_licenses", response_model=List[str])
def get_unlisted_licenses():
    """
    Returns a list of all distinct license URLs for images that do NOT have any known license URLs,
    and that are themselves not known.
    """
    known_urls = known_license_urls()
    database = DatabaseRepository()
    with database.session_scope() as session:
        # Get all images
        images = session.exec(select(Image)).all()
        unlisted_urls = set()

        for image in images:
            # Fetch all licenses for this image
            statement = select(License).where(License.parent_image_id == image.id)
            licenses = session.exec(statement).all()# Flatten license urls for this image
            image_urls = {url for license in licenses for url in (license.urls or [])}
            # If any known url in image_urls, skip this image
            if any(url in known_urls for url in image_urls):
                continue
            # Add unlisted (unknown) urls
            unlisted_urls.update(url for url in image_urls if url not in known_urls)

        sorted_urls = sorted(unlisted_urls)
        return sorted_urls

# Assuming this is in your main API file where other endpoints are defined
@app.get("/api/thumbnail/{image_name}")
async def get_thumbnail(image_name: str):
    thumbnail_service = ThumbnailService()
    thumbnail_path = thumbnail_service.thumbnail_url(image_name)
    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(thumbnail_path)

@app.get("/api/update")
def update():
    db_repo = DatabaseRepository()
    config = Configuration.load()

    storage_client = Storage(config.google_project_id, config.google_bucket_id)
    thumbnail_service = ThumbnailService(storage_client, config.thumbnail)
    sync_images(storage_client, db_repo)

    # only call this when adding new images
    update_thumbnails(db_repo, thumbnail_service)

    #update_licenses(db_repo)

    # one time thing:
    fix_unique_licenses(db_repo)

    update_images(db_repo, max_search_results=config.max_search_results)
    update_licenses(db_repo)
    #report(db_repo)



def generate_sheet(config, match_count):
    """Generate Google Sheet from the database"""
    print("Generating Google Sheet from database...")
    sheet_generator = GoogleSheetFromDatabase(config.spreadsheet, match_count)
    spreadsheet_id = sheet_generator.populate_sheet()
    style_sheet(sheet_generator.sheet, sheet_generator.header_spec, config.sheet_style)
    print(f"Spreadsheet complete: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
    return spreadsheet_id


# Mount frontend static files if they exist (for production)
dist_path = Path(__file__).parent.parent / "web-ui" / "dist"
if dist_path.exists():
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")


if __name__ == "__main__":
    sort_license_urls(DatabaseRepository(), mock=True)