import re
from time import sleep
import gspread
from typing import List, Optional, Tuple
from gspread.exceptions import APIError
from pydantic import BaseModel
from sqlmodel import select, SQLModel, Field

from backend.database.repository import DatabaseRepository
from backend.google_apis.drive import get_drive_service
from backend.google_apis.storage import Storage
from licensing.config import Configuration
from main import DATA_PATH
from backend.model.image import Image
from backend.model.match import Match

class Sheet(SQLModel, table=True):
    __tablename__ = "sheets"

    id: str = Field(primary_key=True)


class SheetMatch(BaseModel):
    """Represents a match found in a Google Sheet."""
    matching_number: Optional[int] = None
    matching_type: str
    image_url: str
    page_url: str
    title: str

class SheetImage(BaseModel):
    """Represents an image with its matches from a Google Sheet."""
    name: str
    blob_public_url: str
    number_of_matches: Optional[int] = None
    matches: List[SheetMatch] = []

    def save(self, database: DatabaseRepository, blobs):
        with database.session_scope() as session:
            statement = select(Image).where(Image.name == self.name)
            image = session.exec(statement).one_or_none()
            if image is None:
                blob = blobs.get(self.name)
                if blob is None:
                    if self.name != "image-3.png":
                        print_red(f"Image {self.name} not found in bucket but should have been")
                    return
                image = Image(
                    id=blob.id,
                    name=self.name,
                    bucket_name=blob.bucket.name,
                    matches=[
                        Match(
                            parent_image_id=blob.id,
                            page_url=match.page_url,
                            title=match.title,
                            image_url=match.image_url,
                            matching_type=match.matching_type
                        )
                        for match in self.matches
                    ]
                )
                print(f"New image: {self.name}. Matches: {len(image.matches)}")

            else:
                old_num_matches = len(image.matches)
                new_matches = [
                    Match(
                        parent_image_id=image.id,
                        page_url=match.page_url,
                        title=match.title,
                        image_url=match.image_url,
                        matching_type=match.matching_type
                    )
                    for match in self.matches if match.page_url not in [m.page_url for m in image.matches]
                ]
                if len(new_matches) == 0:
                    return
                image.matches.extend(new_matches)
                new_num_matches = len(image.matches)
                print(f"Existing image: {self.name}. Matches: {new_num_matches} (added: {new_num_matches - old_num_matches})")

            session.add(image)
            for match in image.matches:
                session.add(match)


def find_sheets_in_folder(folder_id: str, drive_service) -> List[dict]:
    """Find Google Sheets in a folder that match the naming criteria."""
    
    # Query for sheets with "Image Licensing" or "image_report" in the name
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and " \
            f"(name contains 'Image Licensing' or name contains 'image_report')"
    
    results = drive_service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()
    
    return results.get("files", [])

def extract_url_from_image_formula(formula: str) -> str:
    """Extract the URL from an =IMAGE() formula."""
    # Pattern to match the URL inside IMAGE()
    pattern = r"=IMAGE\([\"']?(https?://[^\"',)]+)[\"']?"
    match = re.search(pattern, formula)
    if match:
        return match.group(1)
    return ""

def extract_url_and_title_from_hyperlink(formula: str) -> Tuple[str, str]:
    """Extract the URL and title from a =HYPERLINK() formula."""
    # Pattern to match URL and title in HYPERLINK(url, title)
    pattern = r'=HYPERLINK\("((?:[^"]|(?:""))*)"\s*,\s*"((?:[^"]|(?:""))*)"\)'
    match = re.search(pattern, formula)
    if match:
        return match.group(1), match.group(2)
    return "", ""

def parse_single_header_sheet(values, spreadsheet_id, database, blobs) -> List[SheetImage]:
    """Parse a sheet with a single header row."""
    # Get all values
    if len(values) < 2:  # Need at least one row for headers and one row of data
        print_orange("no data")
        return []

    # Get headers (first row)
    headers = values[0]
    
    # Find column indices
    image_col = (
        headers.index("image") if "image" in headers else
        headers.index("source image") if "source image" in headers else
        headers.index("original image") if "original image" in headers else
        None
    )
    name_col = headers.index("name") if "name" in headers else headers.index("image name") if "image name" in headers else None

    if name_col is None:
        print_red(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit: Missing name column")

    # Find all match columns (match i, image i, webpage i)
    match_cols = {}
    for i, header in enumerate(headers):
        split_header = header.split(" ")
        if len(split_header) < 2:
            continue
        index = split_header[1]
        if not index.isdigit():
            continue
        if header.startswith("match "):
            if index not in match_cols:
                match_cols[index] = {"match": i}
            else:
                match_cols[index]["match"] = i
        elif header.startswith("image "):
            if index not in match_cols:
                match_cols[index] = {"image": i}
            else:
                match_cols[index]["image"] = i
        elif header.startswith("webpage ") or header.startswith("source "):
            if index not in match_cols:
                match_cols[index] = {"webpage": i}
            else:
                match_cols[index]["webpage"] = i

    # Parse each row
    for row_idx, row in enumerate(values[1:], 1):  # Skip header
        if row_idx >= len(values):
            break
            return None

        # Create SheetImage
        image = SheetImage(
            name=row[name_col],
            blob_public_url=extract_url_from_image_formula(row[image_col]),
            number_of_matches=len(match_cols)
        )
        
        # Add matches
        for index, cols in match_cols.items():
            if "match" in cols and "image" in cols and "webpage" in cols:
                match_col = cols["match"]
                image_col = cols["image"]
                webpage_col = cols["webpage"]
                
                # Skip if any cell is empty
                if (row_idx < len(values) and 
                    match_col < len(row) and image_col < len(row) and webpage_col < len(row) and
                    row[match_col] and row[image_col] and row[webpage_col]):

                    # Extract URLs from formulas
                    image_url = extract_url_from_image_formula(row[image_col])
                    page_url, title = extract_url_and_title_from_hyperlink(row[webpage_col])

                    if not page_url and not title:
                        print_red(f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit: Missing title or URL in 'webpage' column {col_num_to_letter(webpage_col)} for match {index} in row {row_idx + 1}")

                    if page_url and not title:
                        title = page_url

                    match = SheetMatch(
                        matching_number=int(index) if index.isdigit() else None,
                        matching_type=row[match_col],
                        image_url=image_url,
                        page_url=page_url,
                        title=title
                    )
                    image.matches.append(match)
                elif not row[match_col] and not row[image_col] and not row[webpage_col]:
                    pass
                else:
                    print_red(f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit: Some but not all missing cells in columns {col_num_to_letter(match_col)}, {col_num_to_letter(image_col)} or {col_num_to_letter(webpage_col)} in row {row_idx + 1}")
            else:
                print_red(
                    f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit: Missing columns 'match', 'image' or 'webpage' for match {index} in row {row_idx + 1}")
        image.save(database, blobs)
    return None


def parse_two_header_sheet(values, spreadsheet_id, database, blobs) -> List[SheetImage]:
    """Parse a sheet with two header rows."""
    # Get all values
    if len(values) < 3:
        print_orange("no data")
        # Need at least two rows for headers and one row of data
        return []
    
    # Get headers (first two rows)
    header_row1 = values[0]
    header_row2 = values[1]
    
    # Find column indices for name and number of matches
    name_col = header_row1.index("name") if "name" in header_row1 else None
    num_matches_col = next((i for i, h in enumerate(header_row1) if h.lower() == "number of matches"), None)
    image_col = header_row1.index("image") if "image" in header_row1 else None

    # If name column is missing, return empty list
    if name_col is None:
        print_red(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit: Missing name column")

    # Find all match groups
    match_groups = {}
    current_match = None

    for i, header in enumerate(header_row1):
        # Standardize empty or repeated cells to continue the previous group
        if header.startswith("MATCH "):
            match_num = header.split(" ")[1]
            current_match = match_num
            if match_num not in match_groups:
                match_groups[match_num] = {"start_col": i}
            # Always update end_col to the current index
            match_groups[match_num]["end_col"] = i + 1
        elif header == "" and current_match is not None:
            # Continue current match group for empty cell
            match_groups[current_match]["end_col"] = i + 1
        else:
            current_match = None  # Not a MATCH column or continuation
    
    # Parse each row
    for row_idx, row in enumerate(values[2:], 2):  # Skip headers
        if row_idx >= len(values):
            break
            
        # Create SheetImage
        image = SheetImage(
            name=row[name_col],
            blob_public_url=extract_url_from_image_formula(row[image_col]),
            number_of_matches=int(row[num_matches_col]) if num_matches_col is not None and row[num_matches_col] else None
        )
        
        # Process each match group
        for match_num, cols in match_groups.items():
            start_col = cols["start_col"]
            end_col = cols["end_col"]
            
            # Extract column indices for this match group
            group_headers = header_row2[start_col:end_col]
            
            matching_number_col = None
            matching_type_col = None
            image_col = None
            page_col = None
            
            for col_idx, header in enumerate(group_headers, start_col):
                header_lower = header.lower()
                if header_lower == "matching_number" or header_lower == "matching number" or header_lower == "number":
                    matching_number_col = col_idx
                elif header_lower == "matching_type" or header_lower == "matching type" or header_lower == "match":
                    matching_type_col = col_idx
                elif header_lower == "image":
                    image_col = col_idx
                elif header_lower == "page":
                    page_col = col_idx
            
            # Skip if required columns are missing
            if not (matching_type_col is not None and image_col is not None and page_col is not None):
                print_red(
                    f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit: Missing some of the matching columns 'matching type', 'image' or 'page' for match group {match_num} in row {row_idx + 1}")
                continue
                
            # Skip if any cell is empty
            if (row_idx < len(values) and 
                matching_type_col < len(row) and image_col < len(row) and page_col < len(row) and
                row[matching_type_col] and row[image_col] and row[page_col]):
                
                # Extract URLs from formulas
                image_url = extract_url_from_image_formula(row[image_col])
                page_url, title = extract_url_and_title_from_hyperlink(row[page_col])

                if not page_url and not title:
                    print_red(
                        f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit: Missing title or URL in 'page' column {col_num_to_letter(page_col)} for match {match_num} in row {row_idx + 1}")

                if page_url and not title:
                    title = page_url

                # Get matching number if column exists
                matching_number = None
                if matching_number_col is not None and matching_number_col < len(row) and row[matching_number_col]:
                    try:
                        matching_number = int(row[matching_number_col])
                    except (ValueError, TypeError):
                        pass
                
                # Create match
                match = SheetMatch(
                    matching_number=matching_number,
                    matching_type=row[matching_type_col],
                    image_url=image_url,
                    page_url=page_url,
                    title=title
                )
                image.matches.append(match)
            elif not row[matching_type_col] and not row[image_col] and not row[page_col]:
                pass
            else:
                print_red(
                    f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit: Some but not all missing cells in columns {col_num_to_letter(matching_type_col)}, {col_num_to_letter(image_col)} or {col_num_to_letter(page_col)} in row {row_idx + 1}")
        image.save(database, blobs)
    return None

def parse_sheet(sheet, file_name, database, blobs) -> List[SheetImage]:
    """Parse a sheet, detecting its format and delegating to the appropriate parser."""
    # Get all values
    values = safe_get_all_values(sheet)
    if not values:
        return []
    
    # Check if it's a two-header sheet
    is_two_header = False
    for cell in values[0]:
        if cell.startswith("MATCH "):
            is_two_header = True
            break
    
    if is_two_header:
        print(f"Parsing two-header sheet '{file_name}': https://docs.google.com/spreadsheets/d/{sheet.spreadsheet_id}/edit")
        parse_two_header_sheet(values, sheet.spreadsheet_id, database, blobs)
    else:
        print(f"Parsing single header sheet '{file_name}': https://docs.google.com/spreadsheets/d/{sheet.spreadsheet_id}/edit")
        parse_single_header_sheet(values, sheet.spreadsheet_id, database, blobs)

    # save the sheet to the database so we don't process it again
    with database.session_scope() as session:
        session.add(Sheet(id=sheet.spreadsheet_id))
        print(f"Sheet '{file_name}' parsed successfully: https://docs.google.com/spreadsheets/d/{sheet.spreadsheet_id}/edit")

    return None


def parse_all_sheets_in_folder(folder_id: str, drive_service, credentials, database, blobs) -> List[SheetImage]:
    """Parse all Google Sheets in a folder that match the naming criteria."""
    with database.session_scope() as session:
        statement = select(Sheet.id)
        db_sheets = session.execute(statement).all()
        db_sheet_ids = [sheet.id for sheet in db_sheets]

    # Find non-processed sheets
    all_sheets = find_sheets_in_folder(folder_id, drive_service)
    sheets = [sheet for sheet in all_sheets if sheet["id"] not in db_sheet_ids]

    print(f"Processing {len(sheets)} sheets")
    # Setup Google Sheets API client
    client = gspread.authorize(credentials)
    
    # Parse each sheet
    for sheet_info in sheets:
        sheet_id = sheet_info["id"]
        spreadsheet = client.open_by_key(sheet_id)

        # Process each worksheet in the spreadsheet
        for worksheet in spreadsheet.worksheets():
            parse_sheet(worksheet, spreadsheet.title, database, blobs)

def safe_get_all_values(worksheet):
    max_retries = 5
    backoff = 10  # start with 10 seconds
    for attempt in range(max_retries):
        try:
            # Replace this with your gspread call, e.g. worksheet.get_all_records()
            return worksheet.get_all_values(value_render_option="FORMULA")
        except APIError as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                print_orange(f"Quota exceeded (attempt {attempt + 1}/{max_retries}). Waiting {backoff} seconds.")
                sleep(backoff)
                backoff *= 2  # Exponential backoff
            else:
                raise  # re-raise any other APIError
    raise Exception("Quota limit repeatedly exceeded; aborting operation.")

def col_num_to_letter(n):
    result = ""
    n += 1  # Shift to 1-based for calculation
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(rem + ord('A')) + result
    return result


def print_red(text):
    print(f"\033[31m{text}\033[0m")
    raise Exception(text)

def print_orange(text):
    print(f"\033[33m{text}\033[0m")

def main():
    config = Configuration.load()
    credentials, drive_service = get_drive_service()
    storage_client = Storage(config.google_project_id, config.google_bucket_id)
    database = DatabaseRepository(DATA_PATH)
    blobs_by_name = {blob.name: blob for blob in storage_client.blobs}
    parse_all_sheets_in_folder(folder_id=config.google_folder_id, drive_service=drive_service, credentials=credentials, database=database, blobs=blobs_by_name)

if __name__ == "__main__":
    main()
