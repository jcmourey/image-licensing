from licensing.style_sheet import style_sheet
from google_apis.vision import Vision
from google_apis.sheet import GoogleSheet
from licensing.config import Configuration
from licensing.image import ImageSet
from licensing.sheet_row import SheetRow

def main():
    config = Configuration.load()

    image_set = ImageSet.from_bucket(config.images, config.search)

    match_count = config.sheet_style.match_count
    header_spec = SheetRow.header_spec(match_count)
    sheet = GoogleSheet(config.spreadsheet, header_spec.rows)
    style_sheet(sheet, header_spec, config.sheet_style)

    def publish_image(image):
        sheet.append_row(
            SheetRow
            .from_image(image)
            .values(match_count)
        )

    vision = Vision()
    has_unprocessed_images = True
    while has_unprocessed_images:
        vision.batch_search(image_set, publish_method=publish_image)
        has_unprocessed_images = image_set.eligible_to_get_more_matches()

    print("Spreadsheet complete: https://docs.google.com/spreadsheets/d/" + sheet.spreadsheet_id + "/edit")

if __name__ == "__main__":
    main()