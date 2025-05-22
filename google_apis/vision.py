from google.cloud import vision
from .credentials import get_creds
from .storage import get_gcs_uri
from urllib.parse import urlparse


def get_vision_client():
    creds = get_creds()
    client = vision.ImageAnnotatorClient(credentials=creds)
    return client

vision_client = None


def google_vision_search(blob, max_results):
    global vision_client
    if vision_client is None:
        vision_client = get_vision_client()
    gcs_uri = get_gcs_uri(blob)
    response = vision_client.annotate_image({
        'image': {'source': {'image_uri': gcs_uri}},
        'features': [{'type_': vision.Feature.Type.WEB_DETECTION, 'max_results': max_results}]
    })
    yield parse_vision_response(response)


def google_batch_vision_search(blobs, max_results):
    global vision_client
    if vision_client is None:
        vision_client = get_vision_client()

    responses = []
    blob_index = 1
    for batch in chunk_list(blobs, 16):
        print("Annotating blobs", blob_index, "to", blob_index + len(batch) - 1)
        responses += batch_annotate_gcs_images(batch, vision_client, max_results)
        blob_index += len(batch)
    return responses


def batch_annotate_gcs_images(blobs, client, max_results):
    # gcs_uris: list of up to 16 gs:// URIs
    requests = []
    for blob in blobs:
        uri = get_gcs_uri(blob)
        requests.append({
            'image': {'source': {'image_uri': uri}},
            'features': [{'type_': vision.Feature.Type.WEB_DETECTION, 'max_results': max_results}]
        })
    response = client.batch_annotate_images(requests=requests)
    return response.responses  # List of responses, one per image


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i+chunk_size]


def parse_vision_response(response):
    web_detection = response.web_detection
    matching_images = web_detection.pages_with_matching_images
    if len(matching_images) == 0 or not matching_images:
        visually_similar_images = web_detection.visually_similar_images
        if len(visually_similar_images) == 0 or not visually_similar_images:
            yield None, None, None, "none found"
        for match in visually_similar_images:
            yield match.url, get_filename_from_url(match.url), match.url, "visually similar"

    for match in matching_images:
        if len(match.full_matching_images) > 0:
            matching_image_url = match.full_matching_images[0].url
            matching_type = "full match"
        elif len(match.partial_matching_images) > 0:
            matching_image_url = match.partial_matching_images[0].url
            matching_type = "partial match"
        else:
            continue

        yield match.url, match.page_title, matching_image_url, matching_type


def get_filename_from_url(url):
    parsed = urlparse(url)
    path = parsed.path  # e.g., /02/81502-138-4F315F20/overview-eclipses-Sun-and-the-Moon.jpg
    filename = path.split("/")[-1]
    return filename