from sqlmodel import Session, create_engine, SQLModel, select
from backend.model.image import Image
from backend.model.license import License
from backend.model.match import Match
from pathlib import Path
from contextlib import contextmanager
from backend.utilities.print import print_red

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

    # matches has a unique constraint on parent_image_id and page_url
    # make sure to only save new matches to avoid exceptions
    def save_unique_matches(self, matches: list[Match], image_id: str, requested_web_entities: int, found_web_entities: int):
        with self.session_scope() as session:
            # Save matches
            statement = select(Match.page_url).where(Match.parent_image_id == image_id)
            existing_match_urls = session.exec(statement).all()
            new_matches = [match for match in matches if match.page_url not in existing_match_urls]
            unique_matches = list({m.page_url: m for m in new_matches}.values())
            if len(unique_matches) > 0:
                session.add_all(unique_matches)
                match_with_page_count = len([match for match in unique_matches if match.page_url != match.image_url])
                print(f"Saved {len(unique_matches)} new matches (including {match_with_page_count} with page urls) to database for image {image_id}")
            
            # Update image web entities fields
            image_statement = select(Image).where(Image.id == image_id)
            image = session.exec(image_statement).one_or_none()
            if image:
                old_requested_web_entities = image.web_entities_requested
                old_found_web_entities = image.web_entities_found
                if old_requested_web_entities != requested_web_entities or old_found_web_entities != found_web_entities:
                    image.web_entities_requested = requested_web_entities
                    image.web_entities_found = found_web_entities
                    session.add(image)
                    print(f"Updated web entities for image {image_id}: requested={old_requested_web_entities} -> {requested_web_entities}, found={old_found_web_entities} -> {found_web_entities}")
                else:
                    print(f"Web entities for image {image_id} are already up to date: requested={requested_web_entities}, found={found_web_entities}")
            else:
                print_red(f"Image {image_id} not found in database")

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