from PIL import Image
import io
from pathlib import Path

class ThumbnailService:
    def __init__(self, storage, data_path, config, image_type=".jpg"):
        self.storage = storage
        self.data_path = data_path
        self.thumbnail_size = (config.width, config.height) if config else None
        self.image_type = image_type
        self.ensure_thumbnails_directory()

    @property
    def thumbnails_path(self):
        return self.data_path / Path("thumbnails")

    def ensure_thumbnails_directory(self):
        self.thumbnails_path.mkdir(parents=True, exist_ok=True)

    def image_bytes(self, name):
        return self.storage.download_to_memory(name)

    def thumbnail_url(self, name):
        path = Path(name)
        new_path = self.thumbnails_path / path.with_suffix(self.image_type)
        return new_path

    def update_thumbnail(self, name):
        thumbnail = Thumbnail(self, name)
        thumbnail.update_if_needed()


class Thumbnail:
    def __init__(self, service, name,):
        self.service = service
        self.name = name

    def update_if_needed(self):
        if self.needs_update:
            image_bytes = self.service.image_bytes(self.name)
            self.make(image_bytes)

    @property
    def path(self):
        return self.service.thumbnail_url(self.name)

    @property
    def needs_update(self):
        return not self.existing_has_correct_size

    @property
    def existing_has_correct_size(self):
        return verify_thumbnail_size(self.size, self.service.thumbnail_size)

    @property
    def size(self):
        try:
            size = Image.open(self.path).size
            return size
        except FileNotFoundError as e:
            return None
        except (IOError, OSError, Image.UnidentifiedImageError) as e:
            print(f"Failed to open thumbnail at {self.path}")
            return None

    def make(self, img_bytes):
        with Image.open(io.BytesIO(img_bytes)).convert("RGB") as img:
            img.thumbnail(self.service.thumbnail_size, Image.Resampling.LANCZOS)
            img.save(self.path)
        print(f"Thumbnail saved to {self.path}")

def verify_thumbnail_size(existing, reference):
    return (existing[0] == reference[0] and existing[1] <= reference[1]) or (existing[0] <= reference[0] and existing[1] == reference[1])