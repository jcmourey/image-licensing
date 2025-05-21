from .credentials import get_sheets_service

def resize_sheet(spreadsheet_id, sheet_id, num_rows, image_column_indices, source_column_indices, width, height):
    service = get_sheets_service()

    requests = [
        request_make_first_row_bold(sheet_id),
        request_resize_sheet_rows(sheet_id, 1, num_rows, height)
    ]

    for column_index in image_column_indices + source_column_indices:
        requests.append(request_resize_sheet_columns(sheet_id, column_index, width))

    body = {"requests": requests}
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    return response


def request_resize_sheet_rows(sheet_id, row_start, row_end, height):
    return {
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "ROWS",
                "startIndex": row_start,
                "endIndex": row_end
            },
            "properties": {
                "pixelSize": height
            },
            "fields": "pixelSize"
        }
    }


def request_resize_sheet_columns(sheet_id, col_index, width):
    return {
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "COLUMNS",
                "startIndex": col_index,  # zero-based
                "endIndex": col_index + 1
            },
            "properties": {
                "pixelSize": width
            },
            "fields": "pixelSize"
        }
    }


def request_make_first_row_bold(sheet_id):
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,   # Row 1 (zero-based)
                "endRowIndex": 1,     # Just the first row
            },
            "cell": {
                "userEnteredFormat": {
                    "textFormat": {
                        "bold": True
                    }
                }
            },
            "fields": "userEnteredFormat.textFormat.bold"
        }
    }