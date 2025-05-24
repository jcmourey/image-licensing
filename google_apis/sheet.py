from gspread import authorize
from gspread.utils import ValueInputOption
from urllib.parse import urlparse
from .drive import get_drive_service

class GoogleSheet:
    def __init__(self, config, headers):
        self.creds, self.service = get_drive_service()

        sheet_metadata = {
            'name': config.name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [config.folder_id]
        }
        file = self.service.files().create(body=sheet_metadata, fields='id').execute()
        self.spreadsheet_id = file.get('id')
        self.gc = authorize(self.creds)
        self.sheet = self.gc.open_by_key(self.spreadsheet_id)
        self.worksheet = self.sheet.get_worksheet(0)
        self.headers = headers
        self.worksheet.insert_rows(headers)
        print(f"Google Sheet created at: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit")

    def freeze_header_rows(self, count=1):
        self.worksheet.freeze(count)

    def append_row(self, row):
        next_row = len(self.worksheet.get_all_values()) + 1
        self.worksheet.insert_rows([row], row=next_row, value_input_option=ValueInputOption.user_entered)
        print(f"Appended row {next_row}")


def image_link(url):
    if url is None:
        return "none found"
    return f'=IMAGE("{url}")'


def hyperlink(url, text):
    if url is None or text is None:
        return "not provided"
    return safe_hyperlink(url, text)


def root_hyperlink(url):
    if url is None:
        return "not provided"
    parsed = urlparse(url)
    root_url = f"{parsed.scheme}://{parsed.netloc}"
    return safe_hyperlink(root_url, parsed.netloc)


def safe_hyperlink(url, text):
    url_escaped = url.replace('"', '""')
    text_escaped = text.replace('"', '""')
    return f'=HYPERLINK("{url_escaped}", "{text_escaped}")'