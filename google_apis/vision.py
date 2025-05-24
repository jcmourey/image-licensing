from google.cloud import vision
from licensing.image import ImageMatch
from .credentials import get_creds
from urllib.parse import urlparse


class Vision:
    def __init__(self):
        self.creds = get_creds()
        self.client = vision.ImageAnnotatorClient(credentials=self.creds)

    def batch_search(self, image_set, publish_method):
        eligible_images = [image for image in image_set.images if image.is_eligible_to_get_more_matches]
        # the maximum batch size for Google Vision batch annotation is 16
        image_number = 1
        for batch in chunk_list(eligible_images, 16):
            print("Annotating images", image_number, "to", image_number + len(batch) - 1)
            self.batch_annotate_gcs_images(batch, publish_method)
            image_number += len(batch)

    def batch_annotate_gcs_images(self, images, publish_method):
        requests = [make_request(image, image.match_limit) for image in images]
        response = self.client.batch_annotate_images(requests=requests)
        for image, response in zip(images, response.responses):
            for match in image_matches(response):
                image.add_match(match)
                if image.has_enough:
                    break
            image.publish(publish_method)


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


def image_matches(response):
    web_detection = response.web_detection
    for page in web_detection.pages_with_matching_images:
        for image in page.full_matching_images:
            yield image_match_from_page(page, image, "full match")
        for image in page.partial_matching_images:
            yield image_match_from_page(page, image, "partial match")

    for image in web_detection.full_matching_images:
        yield image_match_from_image(image, "full match")

    for image in web_detection.partial_matching_images:
        yield image_match_from_image(image, "partial match")

    for image in web_detection.visually_similar_images:
        yield image_match_from_image(image, "visually similar")


def image_match_from_page(page, image, match_type):
    return ImageMatch(page.url, page.page_title, image.url, match_type)


def image_match_from_image(image, match_type):
    image_filename = get_filename_from_url(image.url)
    return ImageMatch(image.url, image_filename, image.url, match_type)


def get_filename_from_url(url):
    parsed = urlparse(url)
    path = parsed.path  # e.g., /02/81502-138-4F315F20/overview-eclipses-Sun-and-the-Moon.jpg
    filename = path.split("/")[-1]
    return filename