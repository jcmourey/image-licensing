LICENSES_BY_TYPE = {
    # No attribution required (CC0, public domain marks)
    "No attribution required (CC0, public domain marks)": [
        "https://creativecommons.org/publicdomain/zero/1.0/",
        "https://creativecommons.org/public-domain/",
        "https://creativecommons.org/publicdomain/mark/1.0/",
        "http://creativecommons.org/licenses/publicdomain/",
        "https://creativecommons.org/licenses/publicdomain/",
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
        "https://www.fandom.com/licensing"
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

def get_license_attribution(url: str) -> str:
    """
    Given a Creative Commons license URL, returns the full attribution explanation.
    If the URL is not recognized, returns 'Unknown or unsupported license URL'.
    """
    for attr, urls in LICENSES_BY_TYPE.items():
        if url in urls:
            return attr
    return "Unknown or unsupported license URL"

def known_license_urls() -> set[str]:
    return set(url for urls in LICENSES_BY_TYPE.values() for url in urls)

