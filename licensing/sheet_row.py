from pydantic import BaseModel

from google_apis.sheet import root_hyperlink, image_link, hyperlink


class SheetRowMatch(BaseModel):
    matching_number: int
    matching_type: str
    license: str
    site: str
    page: str
    image: str

    @property
    def values(self):
        return [getattr(self, name) for name in SheetRowMatch.model_fields]

    @classmethod
    def from_match(cls, match):
        return cls(
            matching_number=match.matching_index + 1,
            matching_type=match.matching_type,
            license=match.license.sheet_cell_representation or "skipped (found enough licenses)",
            site=root_hyperlink(match.page_url),
            page=hyperlink(match.page_url, match.title),
            image=image_link(match.image_url)
        )


class HeaderSpec:
    def __init__(self, simple_fields, match_fields, match_count):
        self.simple_fields = simple_fields
        self.match_fields = match_fields
        self.match_count = match_count

    @property
    def header1(self):
        return self.simple_fields + [f"MATCH {i + 1}" for i in range(self.match_count) for _ in self.match_fields]

    @property
    def header2(self):
        return [""] * len(self.simple_fields) + self.match_fields * self.match_count

    @property
    def names(self):
        return self.simple_fields + self.match_fields * self.match_count

    @property
    def rows(self):
        return [self.header1, self.header2]

    @property
    def num_simple_fields(self):
        return len(self.simple_fields)

    @property
    def num_match_fields(self):
        return len(self.match_fields)


class SheetRow(BaseModel):
    image: str
    name: str
    number_of_matches: int
    matches: list[SheetRowMatch]

    @classmethod
    def from_image(cls, image):
        return cls(
            image=image.sheet_cell_representation,
            name=image.name,
            number_of_matches=len(image.matches),
            matches=[SheetRowMatch.from_match(m) for m in image.sorted_matches]
        )

    @classmethod
    def simple_fields(cls):
        return [field for field in cls.model_fields if field != "matches"]

    @classmethod
    def header_spec(cls, match_count):
        match_fields = list(SheetRowMatch.model_fields)
        return HeaderSpec(
            simple_fields=sanitize(cls.simple_fields()),
            match_fields=sanitize(match_fields),
            match_count=match_count
        )

    @property
    def simple_values(self):
        return [getattr(self, name) for name in SheetRow.simple_fields()]

    def values(self, match_count):
        return self.simple_values + [
            value
            for match in self.matches[0:match_count]
            for value in match.values
        ]





def sanitize(fields: list[str]):
    return [field.replace('_url', '').replace('_', ' ') for field in fields]