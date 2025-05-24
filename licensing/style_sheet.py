from licensing.config_model import Width
from google_apis.sheet_styling import GoogleSheetStyle


def style_sheet(sheet, header_spec, sheet_style):
    num_header_rows = len(sheet.headers)
    sheet.freeze_header_rows(num_header_rows)

    column_indices = {k: find_column_indices(header_spec.names, k) for k in Width.model_fields}

    style = GoogleSheetStyle(sheet.worksheet.id, sheet.spreadsheet_id, sheet.creds)

    # general style characteristics
    style.bold(0, num_header_rows)
    style.horizontal_center()
    style.vertical_middle()
    style.wrap_cells()
    style.resize_rows(height=sheet_style.height, row_start=num_header_rows)

    # vertically merge the simple field headers
    style.merge_cells(0, num_header_rows,0, header_spec.num_simple_fields, "MERGE_COLUMNS")

    # horizontally merge the match headers' first row for each match
    for i in range(header_spec.match_count):
        start = header_spec.num_simple_fields + i * header_spec.num_match_fields
        end = start + header_spec.num_match_fields
        style.vertical_border(start)
        style.merge_cells(0, 1, start, end, "MERGE_ROWS")

    # apply column widths
    for column_type in Width.model_fields:
        width = getattr(sheet_style.width, column_type)
        if width is None:
            continue
        for column_index in column_indices[column_type]:
            style.resize_columns(width, column_index)

    style.execute()


def find_column_indices(columns, keyword):
    return [i for i, col in enumerate(columns) if keyword in col.lower()]