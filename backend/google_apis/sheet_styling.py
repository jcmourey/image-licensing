from googleapiclient.discovery import build

class GoogleSheetStyle:
    def __init__(self, worksheet_id, spreadsheet_id, creds):
        self.worksheet_id = worksheet_id
        self.spreadsheet_id = spreadsheet_id
        self.service = build('sheets', 'v4', credentials=creds)
        self.requests = []

    def execute(self):
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                "requests": self.requests
            }
        ).execute()
        self.requests = []

    def resize_rows(self, height, row_start=0, row_end=None):
        request = resize(
            self.dimension_range("ROWS", row_start, row_end),
            height
        )
        self.requests.append(request)

    def resize_columns(self, width, col_index):
        request = resize(
            self.dimension_range( "COLUMNS", col_index, col_index + 1),
            width
        )
        self.requests.append(request)

    def dimension_range(self, dimension, start_index, end_index):
        # dimension is either ROWS or COLUMNS
        return {
            "sheetId": self.worksheet_id,
            "dimension": dimension,
            "startIndex": start_index,
            "endIndex": end_index
        }

    def bold(self, start_row=0, end_row=None, start_col=0, end_col=None):
        request = cell_format(
            self.grid_range(start_row, end_row, start_col, end_col),
            {
                "userEnteredFormat": {
                    "textFormat": {
                        "bold": True
                    }
                }
            },
            "userEnteredFormat.textFormat.bold"
        )
        self.requests.append(request)

    def wrap_cells(self, start_row=0, end_row=None, start_col=0, end_col=None):
        request = cell_format(
            self.grid_range(start_row, end_row, start_col, end_col),
            {
                "userEnteredFormat": {
                    "wrapStrategy": "WRAP"
                }
            },
            "userEnteredFormat.wrapStrategy"
        )
        self.requests.append(request)


    def horizontal_center(self, start_row=0, end_row=None, start_col=0, end_col=None):
        request = cell_format(
            self.grid_range(start_row, end_row, start_col, end_col),
            {
                "userEnteredFormat": {
                    "horizontalAlignment": "CENTER"
                }
            },
            "userEnteredFormat.horizontalAlignment"
        )
        self.requests.append(request)

    def vertical_middle(self, start_row=0, end_row=None, start_col=0, end_col=None):
        request = cell_format(
            self.grid_range(start_row, end_row, start_col, end_col),
            {
                "userEnteredFormat": {
                    "verticalAlignment": "MIDDLE"
                }
            },
            "userEnteredFormat.verticalAlignment"
        )
        self.requests.append(request)

    def vertical_border(self, before_col, start_row=0, end_row=None):
        # Adds thick borders to the left of before_col, for all rows between start_row and end_row
        request = {
            "updateBorders": {
                "range": self.grid_range(start_row, end_row, before_col, before_col + 1),
                "left": {
                    "style": "SOLID_THICK",
                    "color": {"red": 0, "green": 0, "blue": 0}
                }
            }
        }
        self.requests.append(request)

    def grid_range(self, start_row=0, end_row=None, start_col=0, end_col=None):
        cell_range = {
            "sheetId": self.worksheet_id,
            "startRowIndex": start_row,
            "startColumnIndex": start_col,
        }
        if end_row is not None:
            cell_range["endRowIndex"] = end_row
        if end_col is not None:
            cell_range["endColumnIndex"] = end_col
        return cell_range

    def merge_cells(self, start_row, end_row, start_col, end_col, mergeType="MERGE_ALL"):
        request = {
            "mergeCells": {
                "range": {
                    "sheetId": self.worksheet_id,  # Sheet/tab id, not spreadsheet id
                    "startRowIndex": start_row,
                    "endRowIndex": end_row,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col,
                },
                "mergeType": mergeType
            }
        }
        self.requests.append(request)


def resize(cell_range, pixel_size):
    return {
        "updateDimensionProperties": {
            "range": cell_range,
            "properties": {
                "pixelSize": pixel_size
            },
            "fields": "pixelSize"
        }
    }


def cell_format(cell_range, format_info, fields):
    return {
        "repeatCell": {
            "range": cell_range,
            "cell": format_info,
            "fields": fields
        }
    }


