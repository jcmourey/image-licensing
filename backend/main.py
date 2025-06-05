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
from backend.google_apis.vision import Vision
from backend.google_apis.sheet_from_db import GoogleSheetFromDatabase
from backend.licensing.config import Configuration
from backend.model.image import Image
from backend.model.image_response import ImageResponse
from backend.model.license import License
from backend.update.sync_images import sync_images
from backend.update.thumbnails import update_thumbnails
from backend.update.report import report
from backend.update.licenses import update_licenses
from backend.model.set import ImageSet
from backend.database.repository import DatabaseRepository


app = FastAPI()

# Allow frontend dev server to call the API (only needed in dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example route
@app.get("/api/health")
def health_check():
    print("Health check")
    return {"status": "ok"}

DATA_PATH = Path("backend/data")

@app.get("/api/images")
def get_images():
    print("Fetching images from database")
    database = DatabaseRepository(data_path=DATA_PATH)
    with database.session_scope() as session:
        statement = select(Image)
        images = session.exec(statement).all()
        response = []
        for image in images:
            statement = select(License).where(License.parent_image_id == image.id)
            licenses = session.exec(statement).all()
            license_count = len(licenses)

            statement = select(License.urls).where(License.parent_image_id == image.id and len(License.urls) > 0)
            license_urls_nested = session.exec(statement).all()
            license_urls = list(dict.fromkeys([url for sublist in license_urls_nested for url in sublist if sublist]))
            license_urls.sort(key=lambda x: "creativecommons.org" in x, reverse=True)

            image_response = ImageResponse(
                id=image.id,
                name=image.name,
                thumbnail_url=f"/api/thumbnail/{image.name}",
                match_count=len(image.matches),
                license_count=license_count,
                license_urls=license_urls,
                has_creative_commons_license=any(license.is_creative_commons_license for license in licenses)
            )
            response.append(image_response)
    response.sort(key=lambda x: (x.has_creative_commons_license, len(x.license_urls)), reverse=True)
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
    config = Configuration.load()

    storage_client = Storage(config.google_project_id, config.google_bucket_id)
    thumbnail_service = ThumbnailService(storage_client, DATA_PATH, config.thumbnail)
    image_set = ImageSet(
        storage=storage_client,
        database=db_repo,
        thumbnail_service=thumbnail_service,
        max_matches=config.max_search_results
    )
    sync_images(storage_client, db_repo)
    update_thumbnails(db_repo, thumbnail_service)
    update_licenses(db_repo)
    report(db_repo)

    vision = Vision(publish=db_repo.save_unique_matches)
    #
    # while not image_set.is_complete:
    #     process_images = image_set.eligible_images
    #     vision.batch_search(image_set)

    # print("Database updated successfully")


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