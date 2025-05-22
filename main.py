import os
import json
from google_apis.vision import google_batch_vision_search, parse_vision_response
from license import extract_page_license_metadata
from google_apis.sheet import save_sheet, insert_image, insert_hyperlink, insert_root_hyperlink
from google_apis.storage import get_bucket_blobs
import column

CONFIG_PATH = "config.json"


def main():
    config = load_config()
    google_cfg = config.get("google", {})

    bucket_name = google_cfg.get("storage", {}).get("bucket", "")
    project_name = google_cfg.get("project", "")
    max_results = google_cfg.get("vision", "").get("max_results", 3)

    blobs = get_bucket_blobs(bucket_name, project_name)
    responses = google_batch_vision_search(blobs, max_results)

    rows = []
    blob_number = 1
    for blob, response in zip(blobs, responses):
        print("Processing blob", blob_number, "of", len(blobs))
        row = make_row(blob_number, blob, response)
        rows.append(row)
        blob_number += 1

    google_drive_cfg = google_cfg.get("drive", {})
    report_name = google_drive_cfg.get("image_report", "image_report")
    google_folder_id = google_drive_cfg.get("folder_id", "")
    save_sheet(rows, google_folder_id, spreadsheet_name=report_name)


def expand_path(path):
    return os.path.expanduser(path)


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def make_row(blob_number, blob, response):
    row = {
        column.NUMBER: blob_number,
        column.IMAGE: insert_image(blob.public_url),
    }

    matches = []
    for page_url, title, image_url, matching_type in parse_vision_response(response):
        license_info, license_error = extract_page_license_metadata(page_url)
        if license_info:
            print("license info for", page_url, ":", license_info)
        matches.append({
            "page_url": page_url,
            "title": title,
            "image_url": image_url,
            "matching_type": matching_type,
            "license_info": license_info,
            "license_error": license_error
        })

    matches_sorted = sorted(matches, key=sort_key)
    for match_index, match in enumerate(matches_sorted):
        fill_row(row, match_index + 1, match)

    row[column.NAME] = blob.name
    return row


# Original list: matches = [(page_url, title, image_url, matching_type, license_info, license_error), ...]
# This will sort so that:
# - has_http==True comes first (not has_http==False)
# - has_license==True comes next (not has_license==False)
# - original order is preserved otherwise (Python sort is stable)
def sort_key(match):
    license_info = match["license_info"]
    # 1. True if 'http' in license_info (license_info can be None)
    has_http = bool(license_info and 'http' in license_info)
    # 2. True if license_info is not None
    has_license = license_info is not None
    # 3. The index, for stable sorting (original order)
    return not has_http, not has_license


def fill_row(row, match_number, match):
    row[f"{column.MATCH} {match_number}"] = match["matching_type"]
    row[f"{column.IMAGE} {match_number}"] = insert_image(match["image_url"])
    row[f"{column.LICENSE} {match_number}"] = match["license_info"] if match["license_info"] else match["license_error"]
    row[f"{column.WEBSITE} {match_number}"] = insert_root_hyperlink(match["page_url"])
    row[f"{column.WEBPAGE} {match_number}"] = insert_hyperlink(match["page_url"], match["title"])


if __name__ == "__main__":
    main()