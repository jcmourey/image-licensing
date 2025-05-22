import gspread
from .credentials import get_drive_service
from .spreadsheet_resize import resize_sheet


def save_spreadsheet(dicts: list[dict], folder_id, spreadsheet_name):
    creds, service = get_drive_service()

    sheet_metadata = {
        'name': spreadsheet_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [folder_id]
    }

    file = service.files().create(body=sheet_metadata, fields='id').execute()
    spreadsheet_id = file.get('id')

    # --- Open the sheet and write data ---
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(0)
    sheet_id = worksheet.id

    data, image_column_indices, source_column_indices = convert_list_of_dicts(dicts)
    worksheet.update(data, value_input_option="USER_ENTERED")

    num_rows = len(data)
    resize_sheet(spreadsheet_id, sheet_id, num_rows, image_column_indices, source_column_indices, width=300, height=round(300*9/16))

    sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    print(f"Google Sheet created at: {sheet_url}")


def convert_list_of_dicts(dicts: list[dict]):
    if not dicts:
        return [], [], []

    columns = list(dicts[0].keys())
    rows = [columns]
    for d in dicts:
        row = [d.get(col, "") for col in columns]
        rows.append(row)
    # Find indices of columns whose name includes "image" (case-insensitive)
    image_column_indices = [i for i, col in enumerate(columns) if "image" in col.lower()]
    source_column_indices = [i for i, col in enumerate(columns) if "source" in col.lower()]
    return rows, image_column_indices, source_column_indices


def insert_image(image_url):
    if image_url is None:
        return "none found"
    return f'=IMAGE("{image_url}")'

def insert_hyperlink(url, text):
    if url is None or text is None:
        return "not provided"
    return f'=HYPERLINK("{url}", "{text}")'