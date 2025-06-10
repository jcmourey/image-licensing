from sqlalchemy import func
from sqlmodel import select
from backend.model.image import Image

def sync_images(storage, database):
    # sync blobs from storage to images from the database
    blobs_by_id = storage.blobs_by_id
    blob_ids = blobs_by_id.keys()

    with database.session_scope() as session:
        statement = select(Image.id)
        db_ids = session.exec(statement).all()

        new = [id for id in blob_ids if id not in db_ids]
        obsolete = [id for id in db_ids if id not in blob_ids]

        if len(new) > 0:
            max_number = session.exec(select(func.max(Image.number))).one()
            next_number = (max_number or 0) + 1

            new_images = []
            for blob_id in new:
                new_image = Image(
                    id=blob_id,
                    number=next_number,
                    name=blobs_by_id[blob_id].name,
                    bucket_name=blobs_by_id[blob_id].bucket.name,
                )
                next_number += 1
                new_images.append(new_image)

            session.add_all(new_images)
            print(f"Added {len(new_images)} new images to database")
        else:
            print("No new images to add")

        if len(obsolete) > 0:
            statement = select(Image).where(Image.id.in_(obsolete))
            images_to_delete = session.exec(statement).all()
            for image in images_to_delete:
                session.delete(image)
            print(f"Deleted {len(obsolete)} images from database")
        else:
            print("No obsolete images to delete")

