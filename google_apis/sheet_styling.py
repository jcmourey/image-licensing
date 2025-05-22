from .credentials import get_sheets_service
import column

def style_sheet(spreadsheet_id, sheet_id, num_rows, columns):
    service = get_sheets_service()
    column_indices, style_table = column.make_style_info(columns)

    requests = [
        request_bold(sheet_id, 0, 1),
        request_horizontal_center(sheet_id),
        request_vertical_middle(sheet_id),
        request_wrap_cells(sheet_id),
        request_resize_rows(sheet_id, 1, num_rows, style_table["height"]),
    ]

    widths = style_table.get("width", {})
    for column_type in widths:
        width = widths[column_type]
        if width is None:
            continue
        for column_index in column_indices[column_type]:
            requests.append(request_resize_columns(sheet_id, column_index, width))

    for match_column_index in column_indices[column.MATCH]:
        requests.append(request_vertical_border(sheet_id, match_column_index))

    body = {"requests": requests}
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    return response


def request_resize_rows(sheet_id, row_start, row_end, height):
    return request_resize(
        dimension_range(sheet_id, "ROWS", row_start, row_end),
        height
    )


def request_resize_columns(sheet_id, col_index, width):
    return request_resize(
        dimension_range(sheet_id, "COLUMNS", col_index, col_index + 1),
        width
    )


def request_resize(cell_range, pixel_size):
    return {
        "updateDimensionProperties": {
            "range": cell_range,
            "properties": {
                "pixelSize": pixel_size
            },
            "fields": "pixelSize"
        }
    }


def request_bold(sheet_id, start_row=0, end_row=None, start_col=0, end_col=None):
    return request_cell_format(
        grid_range(sheet_id, start_row, end_row, start_col, end_col),
        {
            "userEnteredFormat": {
                "textFormat": {
                    "bold": True
                }
            }
        },
        "userEnteredFormat.textFormat.bold"
    )


def request_wrap_cells(sheet_id, start_row=0, end_row=None, start_col=0, end_col=None):
    return request_cell_format(
        grid_range(sheet_id, start_row, end_row, start_col, end_col),
        {
            "userEnteredFormat": {
                "wrapStrategy": "WRAP"
            }
        },
        "userEnteredFormat.wrapStrategy"
    )


def request_horizontal_center(sheet_id, start_row=0, end_row=None, start_col=0, end_col=None):
    return request_cell_format(
        grid_range(sheet_id, start_row, end_row, start_col, end_col),
        {
            "userEnteredFormat": {
                "horizontalAlignment": "CENTER"
            }
        },
        "userEnteredFormat.horizontalAlignment"
    )


def request_vertical_middle(sheet_id, start_row=0, end_row=None, start_col=0, end_col=None):
    return request_cell_format(
        grid_range(sheet_id, start_row, end_row, start_col, end_col),
        {
            "userEnteredFormat": {
                "verticalAlignment": "MIDDLE"
            }
        },
        "userEnteredFormat.verticalAlignment"
    )


def request_cell_format(cell_range, cell_format, fields):
    return {
        "repeatCell": {
            "range": cell_range,
            "cell": cell_format,
            "fields": fields
        }
    }

def request_vertical_border(sheet_id, before_col, start_row=0, end_row=None):
    # Adds thick borders to the left of before_col, for all rows between start_row and end_row
    return {
            "updateBorders": {
                "range": grid_range(sheet_id, start_row, end_row, before_col, before_col + 1),
                "left": {
                    "style": "SOLID_THICK",
                    "color": {"red": 0, "green": 0, "blue": 0}
                }
            }
        }


def dimension_range(sheet_id, dimension, start_index, end_index):
    # dimension is either ROWS or COLUMNS
    return {
        "sheetId": sheet_id,
        "dimension": dimension,
        "startIndex": start_index,
        "endIndex": end_index
    }


def grid_range(sheet_id, start_row=0, end_row=None, start_col=0, end_col=None):
    cell_range = {
        "sheetId": sheet_id,
        "startRowIndex": start_row,
        "startColumnIndex": start_col,
    }
    if end_row is not None:
        cell_range["endRowIndex"] = end_row
    if end_col is not None:
        cell_range["endColumnIndex"] = end_col
    return cell_range
