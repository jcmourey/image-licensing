NUMBER = "#"
IMAGE = "image"
WEBPAGE = "webpage"
WEBSITE = "website"
MATCH = "match"
LICENSE = "license"
NAME = "name"

COLUMNS = [NUMBER, IMAGE, WEBPAGE, WEBSITE, MATCH, LICENSE, NAME]

IMAGE_WIDTH = 300
IMAGE_HEIGHT = round(IMAGE_WIDTH * 9 / 16)


def make_style_info(columns):
    column_indices = {k: find_column_indices(columns, k) for k in COLUMNS}
    style_table = {
        "width": {
            NUMBER: 50,
            IMAGE: IMAGE_WIDTH,
            WEBPAGE: 300,
            WEBSITE: 200,
            MATCH: 100,
            LICENSE: 250,
            NAME: 400
        },
        "height": IMAGE_HEIGHT,
    }
    return column_indices, style_table


def find_column_indices(columns, keyword):
    return [i for i, col in enumerate(columns) if keyword in col.lower()]
