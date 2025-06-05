from .sheet import GoogleSheet, root_hyperlink, image_link, hyperlink
from backend.database.repository import DatabaseRepository
from backend.licensing.sheet_row import HeaderSpec

class GoogleSheetFromDatabase:
    def __init__(self, config, match_count):
        self.db_repo = DatabaseRepository()
        self.match_count = match_count
        
        # Create header specification
        self.header_spec = self._create_header_spec()
        
        # Initialize Google Sheet
        self.sheet = GoogleSheet(config, self.header_spec.rows)
        
    def _create_header_spec(self):
        """Create header specification similar to SheetRow.header_spec"""
        simple_fields = ['IMAGE', 'NAME', 'NUMBER OF MATCHES']
        match_fields = ['MATCHING NUMBER', 'MATCHING TYPE', 'LICENSE', 'SITE', 'PAGE', 'IMAGE']
        return HeaderSpec(simple_fields, match_fields, self.match_count)
    
    def populate_sheet(self):
        """Populate Google Sheet with data from the database"""
        images = self.db_repo.get_all_images()
        
        for image in images:
            row_values = self._create_row_values(image)
            self.sheet.append_row(row_values)
            
        return self.sheet.spreadsheet_id
    
    def _create_row_values(self, image):
        """Create row values for a sheet from a database image record"""
        # Add simple fields first
        row_values = [
            image.image_representation,
            image.name,
            image.number_of_matches
        ]
        
        # Add match fields for each match
        for match in image.matches[:self.match_count]:
            row_values.extend([
                match.matching_number,
                match.matching_type,
                match.license,
                root_hyperlink(match.site),
                hyperlink(match.page_url, match.title),
                image_link(match.image_url)
            ])
            
        return row_values
