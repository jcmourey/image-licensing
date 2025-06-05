from google.cloud import vision
from .credentials import get_creds
from urllib.parse import urlparse
from backend.model.match import Match


class Vision:
    def __init__(self, publish):
        self.creds = get_creds()
        self.client = vision.ImageAnnotatorClient(credentials=self.creds)
        self.publish = publish

    def batch_search(self, image_set):
        # the maximum batch size for Google Vision batch annotation is 16
        image_number = 1
        for batch in chunk_list(image_set.eligible_images, 16):
            print("Annotating images", image_number, "to", image_number + len(batch) - 1)
            self.batch_annotate_gcs_images(batch)
            image_number += len(batch)

    def batch_annotate_gcs_images(self, images):
        requests = [make_request(image, image.match_limit) for image in images]
        response = self.client.batch_annotate_images(requests=requests)
        for image, response in zip(images, response.responses):
            for match in image_matches(response, image.id):
                self.publish(match)
                if image.has_enough:
                    break



def make_request(image, max_results):
    return vision.AnnotateImageRequest(
        image=vision.Image(
            source=vision.ImageSource(image_uri=image.gcs_uri)
        ),
        features=[
            vision.Feature(
                type_=vision.Feature.Type.WEB_DETECTION,
                max_results=max_results
            )
        ]
    )


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i+chunk_size]


def image_matches(response, image_id):
    web_detection = response.web_detection
    for page in web_detection.pages_with_matching_images:
        for image in page.full_matching_images:
            yield image_match_from_page(image_id, page, image,  "full match")
        for image in page.partial_matching_images:
            yield image_match_from_page(image_id, page, image, "partial match")

    for image in web_detection.full_matching_images:
        yield image_match_from_image(image_id, image, "full match")

    for image in web_detection.partial_matching_images:
        yield image_match_from_image(image_id, image, "partial match")

    for image in web_detection.visually_similar_images:
        yield image_match_from_image(image_id, image, "visually similar")


def image_match_from_page(image_id, page, image, matching_type):
    return Match(
        parent_image_id=image_id,
        page_url=page.url,
        title=page.page_title,
        image_url=image.url,
        matching_type=matching_type
    )


def image_match_from_image(image_id, image, matching_type):
    image_filename = get_filename_from_url(image.url)
    return Match(
        parent_image_id=image_id,
        page_url=image.url,
        title=image_filename,
        image_url=image.url,
        matching_type=matching_type
    )


def get_filename_from_url(url):
    parsed = urlparse(url)
    path = parsed.path  # e.g., /02/81502-138-4F315F20/overview-eclipses-Sun-and-the-Moon.jpg
    filename = path.split("/")[-1]
    return filename or url