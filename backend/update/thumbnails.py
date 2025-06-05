from sqlmodel import select
from backend.model.image import Image

def update_thumbnails(database, thumbnail_service):
    with database.session_scope() as session:
        statement = select(Image)
        images = session.exec(statement).all()
        print(f"Updating {len(images)} thumbnails as needed...")
        for image in images:
            thumbnail_service.update_thumbnail(image.name)
