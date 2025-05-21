import os
import json
from google_apis.vision import google_batch_vision_search, parse_vision_response
from license import extract_page_license_metadata
from google_apis.spreadsheet import save_spreadsheet, insert_image, insert_hyperlink
from google_apis.storage import get_bucket_blobs

# --- Configuration ---
CONFIG_PATH = "config.json"

# --- IMAGE TYPES ---
IMAGE_FILE = "file"
IMAGE_CLIPBOARD = "clipboard"

def expand_path(path):
    return os.path.expanduser(path)

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def make_row(blob_number, blob, response):
    row = {
        "number": blob_number,
        "original image": insert_image(blob.public_url),
    }

    match_index = 0
    for page_url, title, image_url, matching_type in parse_vision_response(response):
        match_index += 1
        license_info = extract_page_license_metadata(page_url)
        print("license info for", page_url, ":", license_info)
        row[f"image {match_index}"] = insert_image(image_url)
        row[f"match {match_index}"] = matching_type
        row[f"license {match_index}"] = license_info
        row[f"source {match_index}"] = insert_hyperlink(page_url, title)

    row["name"] = blob.name
    return row


def main():
    config = load_config()
    google_cfg = config.get("google", {})
    google_drive_cfg = google_cfg.get("drive", {})

    bucket_name = google_cfg.get("storage", {}).get("bucket", "")
    project_name = google_cfg.get("project", "")

    blobs = get_bucket_blobs(bucket_name, project_name)
    responses = google_batch_vision_search(blobs)

    rows = []
    blob_number = 1
    for blob, response in zip(blobs, responses):
        print("Processing blob", blob_number, "of", len(blobs))
        row = make_row(blob_number, blob, response)
        rows.append(row)
        blob_number += 1

    report_name = google_drive_cfg.get("image_report", "image_report")
    google_folder_id = google_drive_cfg.get("folder_id", "")
    save_spreadsheet(rows, google_folder_id, spreadsheet_name=report_name)


if __name__ == "__main__":
    main()