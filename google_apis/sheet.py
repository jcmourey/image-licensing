import gspread
from .credentials import get_drive_service
from .sheet_styling import style_sheet
from urllib.parse import urlparse


def save_sheet(dicts: list[dict], folder_id, spreadsheet_name):
    creds, service = get_drive_service()

    sheet_metadata = {
        'name': spreadsheet_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [folder_id]
    }

    file = service.files().create(body=sheet_metadata, fields='id').execute()
    sheet_id = file.get('id')

    # --- Open the sheet and write data ---
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(sheet_id)
    worksheet = sheet.get_worksheet(0)

    data = convert_list_of_dicts(dicts)
    worksheet.update(data, value_input_option="USER_ENTERED")

    num_rows = len(data)
    columns = data[0]
    style_sheet(sheet_id, worksheet.id, num_rows, columns)

    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    print(f"Google Sheet created at: {sheet_url}")


def convert_list_of_dicts(dicts: list[dict]):
    if not dicts:
        return [], [], []

    columns = list(dicts[0].keys())
    rows = [columns]
    for d in dicts:
        row = [d.get(col, "") for col in columns]
        rows.append(row)
    return rows


def insert_image(image_url):
    if image_url is None:
        return "none found"
    return f'=IMAGE("{image_url}")'


def insert_hyperlink(url, text):
    if url is None or text is None:
        return "not provided"
    return make_safe_hyperlink(url, text)


def insert_root_hyperlink(url):
    if url is None:
        return "not provided"
    parsed = urlparse(url)
    root_url = f"{parsed.scheme}://{parsed.netloc}"
    return make_safe_hyperlink(root_url, parsed.netloc)


def make_safe_hyperlink(url, text):
    # Escape quotes for Excel formula: replace " with ""
    url_escaped = url.replace('"', '""')
    text_escaped = text.replace('"', '""')
    return f'=HYPERLINK("{url_escaped}", "{text_escaped}")'