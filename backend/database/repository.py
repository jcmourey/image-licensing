from sqlmodel import Session, create_engine, SQLModel, select
from backend.model.image import Image
from backend.model.license import License
from backend.model.match import Match
from pathlib import Path
from contextlib import contextmanager

class DatabaseRepository:
    def __init__(self, data_path):
        self.db_path = data_path / Path("database.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        SQLModel.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations.

        Usage:
        with session_scope() as session:
        """
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save_new_images(self, images: list[Image]):
        with self.session_scope() as session:
            session.add_all(images)
            print(f"Saved {len(images)} images to database")

    def save_image(self, image: Image):
        with self.session_scope() as session:
            session.add(image)
            print(f"Saved {image.name} to database")

    def delete_images(self, image_ids: list[str]):
        with self.session_scope() as session:
            statement = select(Image).where(Image.id.in_(image_ids))
            images_to_delete = session.exec(statement).all()
            for image in images_to_delete:
                session.delete(image)
        print(f"Deleted {len(image_ids)} images from database")

    def fetch_image_ids(self) -> list[str]:
        with self.session_scope() as session:
            statement = select(Image.id)
            image_ids = session.exec(statement).all()
            return image_ids

    def fetch_image_names(self) -> list[str]:
        with self.session_scope() as session:
            statement = select(Image.name)
            image_ids = session.exec(statement).all()
            return image_ids

    def fetch_images(self) -> dict[str, Image]:
        with self.session_scope() as session:
            statement = select(Image)
            images = session.exec(statement).all()
            return {image.blob_id: image for image in images}

    def save_unique_matches(self, matches: list[Match], image_id: str):
        with self.session_scope() as session:
            statement = select(Match).where(Match.parent_image_id == image_id)
            existing_matches = session.exec(statement).all()
            existing_match_ids = {match.id for match in existing_matches}
            new_matches = [match for match in matches if match.id not in existing_match_ids]
            session.add_all(new_matches)

    def fetch_licenses_by_image_id(self, image_id: str) -> list[License]:
        with self.session_scope() as session:
            statement = select(License).where(License.parent_image_id == image_id)
            licenses = session.exec(statement).all()
            return licenses

    def fetch_image_by_name(self, name: str) -> Image | None:
        with self.session_scope() as session:
            statement = select(Image).where(Image.name == name)
            image = session.exec(statement).one_or_none()
            return image

    # ---- NOT USED YET ----
    def fetch_images_by_blob_ids(self, ids) -> dict[str, Image]:
        with self.session_scope() as session:
            statement = select(Image).where(Image.blob_id.in_(ids))
            images = session.exec(statement).all()
            return {image.blob_id: image for image in images}

    def fetch_images_with_matches(self) -> list[Image]:
        with self.session_scope() as session:
            statement = select(Image).where(Image.matches != None)
            return session.exec(statement).all()

    def fetch_images_with_license_url(self) -> list[Image]:
        with self.session_scope() as session:
            # This query pattern might need to be adjusted based on your actual relationship structure
            statement = select(Image).join(Match).where(Match.license.has(url=None))
            return session.exec(statement).all()