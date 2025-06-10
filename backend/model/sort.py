import re

from backend.licensing.license_types import LICENSES_BY_TYPE

def row_sort_key(row):
    match = row.selected_match or row.best_match
    has_a_match = int(match is not None)

    return (
        -has_a_match,
        sort_key(match.page_url, match.image_url, match.license_url or "", match.matching_type),
    )

def match_sort_key(match):
    preferred_license_url = match.preferred_license_url if match.license else ""
    return sort_key(match.page_url, match.image_url, preferred_license_url or "", match.matching_type)


def sort_key(page_url, image_url, license_url, matching_type):
    # Put "visually similar" at the end
    not_just_visually_similar = int((matching_type or "").lower() != "visually similar")
    # if there is no page_url
    has_a_page_url = int(page_url != image_url)
    # Primary: Priority in LICENSES_BY_TYPE by first license_url

    license_priority = float("inf")
    for idx, urls in enumerate(LICENSES_BY_TYPE.values()):
        if license_url in urls:
            license_priority = idx
            break

    # More accurately detect government domains by checking for .gov followed by /, ., or end of string
    contains_gov_criteria = int(contains_gov(page_url))
    contains_canva_criteria = int(contains_canva(page_url))
    contains_org_criteria = int(contains_org(page_url))
    contains_license = int(bool(re.search(r"license|licensing", license_url, re.I)))
    contains_terms = int("terms" in license_url.lower() and license_url != "/terms")
    contains_stock = int("stock" in license_url.lower())
    return (
        -not_just_visually_similar,
        -has_a_page_url,
        license_priority,
        -contains_canva_criteria,
        -contains_license,
        -contains_terms,
        -contains_gov_criteria,
        -contains_org_criteria,
        -contains_stock,
        page_url or ""
    )


def contains_gov(page_url):
    return contains_suffix(page_url, ".gov")


def contains_org(page_url):
    return contains_suffix(page_url, ".org")


def contains_canva(page_url):
    if page_url is None:
        return False
    return "canva.com" in (page_url or "").lower()


def attribution_explanation(license_url, page_url):
    if not license_url:
        if contains_gov(page_url):
            return "Government domain"
        if contains_canva(page_url):
            return "Canva domain"
        if contains_org(page_url):
            return "Non-Profit domain"
        return None
    for key, url_list in LICENSES_BY_TYPE.items():
        if license_url in url_list:
            return key
    return license_url


def contains_suffix(page_url, suffix):
    if page_url is None:
        return False
    return bool(re.search(suffix + r"($|[\/\.])", (page_url or "").lower()))

