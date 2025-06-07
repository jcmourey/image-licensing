from sqlmodel import select
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from backend.google_apis.storage import Storage
from backend.image_utils.thumbnail import ThumbnailService
from backend.licensing.style_sheet import style_sheet
from backend.google_apis.sheet_from_db import GoogleSheetFromDatabase
from backend.licensing.config import Configuration
from backend.model.image import Image
from backend.model.image_response import ImageResponse
from backend.model.license import License
from backend.model.match import Match
from backend.update.matches import update_images
from backend.update.sync_images import sync_images
from backend.update.thumbnails import update_thumbnails
from backend.update.report import report
from backend.update.licenses import update_licenses, update_approved_licenses, fix_unique_licenses
from backend.database.repository import DatabaseRepository


app = FastAPI()

# Allow frontend dev server to call the API (only needed in dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://macstudiojeancharles.local:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example route
@app.get("/api/health")
def health_check():
    print("Health check")
    return {"status": "ok"}

BACKEND_PATH = Path("backend")
DATA_PATH = BACKEND_PATH / "data"
CONFIG_PATH = BACKEND_PATH / "config.json"

@app.get("/api/images")
def get_images():
    print("Fetching images from database")
    database = DatabaseRepository(data_path=DATA_PATH)
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
    thumbnail_service = ThumbnailService(None, DATA_PATH, None)
    thumbnail_path = thumbnail_service.thumbnail_url(image_name)
    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(thumbnail_path)

@app.get("/api/update")
def update():
    db_repo = DatabaseRepository(data_path=DATA_PATH)
    config = Configuration.load(path=CONFIG_PATH)

    storage_client = Storage(config.google_project_id, config.google_bucket_id)
    thumbnail_service = ThumbnailService(storage_client, DATA_PATH, config.thumbnail)
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
    """Generate Google Sheet from database"""
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

# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)

if __name__ == "__main__":
    get_images()