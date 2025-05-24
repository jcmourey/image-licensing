import os
import tldextract
from config import Configuration
from google_apis.credentials import get_creds
from google_apis.drive import upload_html_to_drive, upload_html_and_thumbs_to_drive
from gspread import authorize
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse

HTML_HEADER = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Image Attribution</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://thespringinstitute.com/wp-content/themes/springinstitute/style.css">
  <style>
  .thumbnail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1.2em;
    margin-top: 2em;
  }
  .thumbnail-grid figure {
    margin: 0;
    background: #f7f7f7;
    border-radius: 10px;
    padding: 1em 0.5em 0.5em 0.5em;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 2px 6px #0001;
    transition: box-shadow 0.2s;
    height: 220px; /* Fixed height for all figures */
    min-width: 0;
    min-height: 0;
    justify-content: flex-end; /* Bottom-align content */
  }
  .thumbnail-grid figure:hover {
    box-shadow: 0 4px 16px #0002;
  }
  .thumbnail-grid img {
    max-width: 110px;
    max-height: 110px;
    border-radius: 7px;
    object-fit: cover;
    margin-bottom: 0.7em;
    box-shadow: 0 1px 4px #0002;
    flex-shrink: 0;
    flex-grow: 0;
  }
  .thumbnail-grid figcaption {
    font-size: 0.95em;
    text-align: center;
    margin: 0;
    width: 100%;
    flex-shrink: 0;
    flex-grow: 0;
    /* Push figcaption to the bottom if content is short */
  }
</style>
</head>
<body>
  <main class="content">
    <h1>Image Attribution</h1>
    <div class="thumbnail-grid">
'''

HTML_FOOTER = '''
    </div>
  </main>
</body>
</html>
'''


class Attribution:
    def __init__(self, image_url, page_url, license_url):
        self.image_url = image_url
        self.page_url = page_url
        self.license_url = license_url

    @classmethod
    def from_image(cls, image):
        best_match = image.sorted_matches[0]
        return cls(
            image_url=image.image_url,
            page_url=best_match.page_url,
            license_url=best_match.license.url
        )


def generate_attribution_html_from_images(images, folder_id):
    attributions = [Attribution.from_image(image) for image in images]
    thumb_paths = download_and_create_thumbnails(attributions)
    HTML_HEADER(attributions, thumb_paths,folder_id)


def get_domain(url):
    ext = tldextract.extract(url)
    # ext.domain: 'creativecommons', ext.suffix: 'org'
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}"
    return url  # fallback


def generate_attribution_html_with_thumbnails(attributions, thumb_urls, folder_id):
    html = [HTML_HEADER]
    for i, (attribution, thumb_url) in enumerate(zip(attributions, thumb_urls)):
        if attribution.license_url:
            root = get_domain(attribution.license_url) or "License"
            license_text = f'<a href="{attribution.license_url}" target="_blank" rel="noopener">{root}</a>'
        else:
            license_text = 'unknown'
        html.append(f'''
              <figure>
                <a href="{attribution.page_url}" target="_blank" rel="noopener">
                  <img src="{thumb_url}" alt="Image {i}">
                </a>
                <figcaption>
                  <a href="{attribution.page_url}" target="_blank" rel="noopener">Source</a>
                  <br />
                  <br />
                  License
                  <br />
                  {license_text}
                </figcaption>
              </figure>
        ''')
    html.append(HTML_FOOTER)
    upload_html_and_thumbs_to_drive(''.join(html), folder_id, thumb_urls)


def get_attributions_from_sheet(sheet_id, worksheet_name):
    creds = get_creds()
    gc = authorize(creds)
    worksheet = gc.open_by_key(sheet_id).worksheet(worksheet_name)
    rows = worksheet.get_all_values(value_render_option='FORMULA')

    attributions = []
    for row in rows[2:]:
        if not row[0]:
            continue
        image_url = extract_image_url(row[0])
        license_url = extract_hyperlink(row[5])
        page_url = extract_hyperlink(row[7])
        attribution = Attribution(image_url, page_url, license_url)
        attributions.append(attribution)
    return attributions


import re

def extract_image_url(cell_value):
    """
    Extracts the URL from a cell containing =IMAGE("url") or returns the value if not a formula.
    """
    if cell_value is None:
        return None
    # If cell contains =IMAGE("...")
    match = re.match(r'=IMAGE\(["\'](.+?)["\']\)', str(cell_value).strip(), re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        return None


def extract_hyperlink(cell_value):
    """
    Extracts the URL from a cell containing =HYPERLINK("url", ...) or returns the value if not a formula.
    """
    if cell_value is None:
        return None
    # If cell contains =HYPERLINK("...")
    match = re.match(r'=HYPERLINK\(["\'](.+?)["\']\s*,', str(cell_value).strip(), re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        return None

THUMB_SIZE = (110, 110)

def download_and_create_thumbnails(attributions, output_dir="thumbnails"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    thumb_paths = []
    for idx, attr in enumerate(attributions):
        thumb_filename = f"thumb_{idx}.jpg"
        thumb_path = os.path.join(output_dir, thumb_filename)
        try:
            resp = requests.get(attr.image_url, timeout=10)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            img.thumbnail(THUMB_SIZE, Image.LANCZOS)
            img.save(thumb_path, format="JPEG")
            thumb_paths.append(thumb_path)
        except Exception as e:
            print(f"Failed to process image {attr.image_url}: {e}")
            thumb_paths.append(None)
    return thumb_paths


if __name__ == '__main__':
    config = Configuration.load()
    attributions = get_attributions_from_sheet("1oM8em0WDjOa6AI-9q3Skz2UmFyvPx8VQ_v1VuEC3Xn8", "Sheet1")
    thumb_paths = download_and_create_thumbnails(attributions)
    generate_attribution_html_with_thumbnails(attributions, thumb_paths, config.spreadsheet.folder_id)