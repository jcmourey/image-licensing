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
from backend.api.image_response import ImageResponse
from backend.model.license import License
from backend.model.match import Match
from backend.update.matches import update_images
from backend.update.sync_images import sync_images
from backend.update.thumbnails import update_thumbnails
from backend.update.licenses import update_licenses, update_approved_licenses, fix_unique_licenses, sort_license_urls
from backend.database.repository import DatabaseRepository
from backend.api import image_rows, comment
import tldextract

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
app.include_router(comment.router)

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
        roots = set()
        for url in urls:
            ext = tldextract.extract(url)
            if ext.domain and ext.suffix:
                roots.add(f"{ext.domain}.{ext.suffix}")
        return roots

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


@app.get("/api/images")
def get_images():
    print("Fetching images from database")
    database = DatabaseRepository()
    with database.session_scope() as session:
        statement = select(Image)
        images = session.exec(statement).all()
        response = []
        for image in images:
            statement = select(License).where(License.parent_image_id == image.id and len(License.urls) > 0)
            licenses = session.exec(statement).all()

            approved_license_urls = list(dict.fromkeys([url for license in licenses for url in license.approved_license_urls]))
            all_license_urls = list(dict.fromkeys([url for license in licenses for url in license.urls]))
            published_licenses = approved_license_urls if len(approved_license_urls) > 0 else all_license_urls

            approved_matches = [license.parent_match for license in licenses if license.approved]
            all_matches = [license.parent_match for license in licenses]
            published_matches = approved_matches if len(approved_matches) > 0 else all_matches
            published_match_page_urls = [match.page_url for match in published_matches]
            published_match_image_urls = [match.image_url for match in published_matches]

            image_response = ImageResponse(
                id=image.id,
                name=image.name,
                thumbnail_url=f"/api/thumbnail/{image.name}",
                match_count=len(image.matches),
                license_urls=published_licenses,
                is_approved=len(approved_license_urls) > 0,
                match_page_urls=published_match_page_urls,
                match_image_urls=published_match_image_urls
            )
            response.append(image_response)
    response.sort(key=lambda x: (x.is_approved, len(x.license_urls)), reverse=True)
    return response

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
    update_approved_licenses(db_repo)

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
    get_image_rows()