from google_apis.sheet import image_link
from google_apis.storage import get_bucket_blobs
from licensing.license import License


class Image:
    def __init__(self, blob, search_config):
        self.blob = blob
        self.matches: list[ImageMatch] = []
        self.search_config = search_config

    @property
    def gcs_uri(self):
        return f"gs://{self.blob.bucket.name}/{self.blob.name}"

    @property
    def name(self):
        return self.blob.name

    def add_match(self, match):
        if match.page_url in [m.page_url for m in self.matches]:
            return
        match.matching_index = len(self.matches)
        match.add_license()
        self.matches.append(match)

    @property
    def has_creative_commons_license(self):
        return any(m.license.is_creative_commons_license for m in self.matches)

    @property
    def has_enough(self):
        return self.has_creative_commons_license

    @property
    def has_license_url(self):
        return any(m.has_license_url for m in self.matches)

    @property
    def has_license_text(self):
        return any(m.has_license_text for m in self.matches)

    @property
    def is_eligible_to_get_more_matches(self):
        return ((not self.has_license_text and len(self.matches) < self.search_config.max_results_for_text) or
                (not self.has_license_url and len(self.matches) < self.search_config.max_results_for_url) or
                (not self.has_creative_commons_license and len(self.matches) < self.search_config.max_results_for_creative_commons))

    @property
    def match_limit(self):
        if self.matches:
            print(f"'{self.blob.name}': adding {self.search_config.result_increment} matches to existing {len(self.matches)}")
        return len(self.matches) + self.search_config.result_increment

    @property
    def sorted_matches(self):
        return sorted(self.matches, key=lambda m: m.sort_key)

    def publish(self, publish_method):
        if not self.is_eligible_to_get_more_matches:
            publish_method(self)

    @property
    def sheet_cell_representation(self):
        return image_link(self.blob.public_url)


class ImageMatch:
    def __init__(self, page_url, title, image_url, matching_type):
        self.page_url = page_url
        self.title = title
        self.image_url = image_url
        self.matching_type = matching_type
        self.matching_index = None
        self.license = None

    def add_license(self):
        self.license = License.extract_page_license_metadata(self.page_url)
        if self.license.is_creative_commons_license:
            print(f"Found CC license for {self.page_url}: {self.license.url}")
        elif self.license.url:
            print(f"Found license URL for {self.page_url}: {self.license.url}")
        elif self.license.text:
            print(f"Found license text for {self.page_url}: {self.license.text}")

    @property
    def has_license_text(self):
        return bool(self.license.text)

    @property
    def has_license_url(self):
        return bool(self.license.url)

    @property
    def sort_key(self):
        return (
            not self.license.is_creative_commons_license,
            not self.license.url,
            not self.license.text
        )


class ImageSet:
    def __init__(self, images):
        self.images = images

    @classmethod
    def from_bucket(cls, image_config, search_config):
        blobs = get_bucket_blobs(image_config.bucket, image_config.project)
        return cls([Image(blob, search_config) for blob in blobs])

    def has_unprocessed_images(self):
        any(i for i in self.images if i.is_eligible_to_get_more_matches)