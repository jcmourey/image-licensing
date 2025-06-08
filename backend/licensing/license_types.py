import re

LICENSES_BY_TYPE = {
    # No attribution required (CC0, public domain marks)
    "No attribution required (CC0, public domain marks)": [
        "https://creativecommons.org/publicdomain/zero/1.0/",
        "https://creativecommons.org/publicdomain/mark/1.0/",
        "https://negativespace.co/license/",
    ],

    # Attribution only (CC BY)
    "Attribution required only (CC BY)": [
        "http://creativecommons.org/licenses/by/4.0/",
        "https://creativecommons.org/licenses/by/4.0/",
        "https://creativecommons.org/licenses/by/2.0",
        "http://creativecommons.org/licenses/by/3.0/",
        "http://creativecommons.org/licenses/by/2.5/hu/",
    ],

    # Attribution + ShareAlike (CC BY-SA)
    "Attribution + ShareAlike required (CC BY-SA)": [
        "https://creativecommons.org/licenses/by-sa/4.0/deed.en",
        "https://creativecommons.org/licenses/by-sa/4.0/",
        "https://creativecommons.org/licenses/by-sa/4.0/?ref=chooser-v1",
        "https://creativecommons.org/licenses/by-sa/4.0/deed.de",
        "https://creativecommons.org/licenses/by-sa/2.0/",
        "https://www.fandom.com/licensing",
    ],

    # Attribution + NonCommercial (CC BY-NC)
    "Attribution + NonCommercial required (CC BY-NC)": [
        "https://creativecommons.org/licenses/by-nc/4.0/",
        "http://creativecommons.org/licenses/by-nc/4.0/",
    ],

    # Attribution + NonCommercial + ShareAlike (CC BY-NC-SA)
    "Attribution + NonCommercial + ShareAlike required (CC BY-NC-SA)": [
        "http://creativecommons.org/licenses/by-nc-sa/4.0/",
        "https://creativecommons.org/licenses/by-nc-sa/2.0/deed.en",
    ],

    # Attribution + NonCommercial + NoDerivs (CC BY-NC-ND)
    "Attribution + NonCommercial + NoDerivs required (CC BY-NC-ND)": [
        "http://creativecommons.org/licenses/by-nc-nd/4.0/",
    ],
}


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


def contains_gov(page_url):
    return contains_suffix(page_url, ".gov")


def contains_org(page_url):
    return contains_suffix(page_url, ".org")


def contains_canva(page_url):
    if page_url is None:
        return False
    return "canva.com" in (page_url or "").lower()


def known_license_urls() -> set[str]:
    return set(url for urls in LICENSES_BY_TYPE.values() for url in urls)

