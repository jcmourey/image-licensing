import re

from sqlalchemy import func
from sqlmodel import select

from backend.database.repository import DatabaseRepository
from backend.licensing.license_types import LICENSES_BY_TYPE
from backend.model.match import Match
from backend.model.license import License


def update_licenses(database):
    with database.session_scope() as session:
        # Match.page_url == Match.image_url means Google Vision didn't return a page for the image
        # TODO figure out a better way to do this (find the license from the root page)
        statement = select(Match).where((None == Match.license) & (Match.page_url != Match.image_url))
        matches = session.exec(statement).all()
        if len(matches) == 0:
            print("No matches to update licenses for")
            return

        print(f"Updating licenses for {len(matches)} matches")
        for match in matches:
            new_license = License.extract_page_license_metadata(match)
            if new_license is not None:
                new_license.urls = list(dict.fromkeys(new_license.urls))
                new_license.urls.sort(key=license_url_sort_key)
                new_license.approved = new_license.is_approved
                session.add(new_license)
                session.commit()
                if len(new_license.meta_info) > 0:
                    print(f"Updated license metadata for match {match.id}: {new_license.meta_info_text}")
                if len(new_license.urls) > 0:
                    print(f"Updated license urls for match {match.id}: {new_license.urls}")
            else:
                print(f"Could not find any license for match {match.id}")


def fix_unique_licenses(database):
    with database.session_scope() as session:
        statement = select(License).where(func.json_array_length(License.urls) > 1)
        licenses = session.exec(statement).all()
        fixed_count = 0
        for license in licenses:
            old_license_urls = license.urls
            license.urls = list(dict.fromkeys(license.urls))
            if old_license_urls != license.urls:
                print(f"Fixed duplicate license URLs for license {license.id}: {len(old_license_urls)} -> {len(license.urls)}")
                session.add(license)
                fixed_count += 1
        print(f"Fixed {fixed_count} duplicate license URLs")


def license_url_sort_key(url: str) -> tuple:
    # 0. Rule out 'http://creativecommons.org/licenses/publicdomain/' which is just a list of their licenses, not an actual license
    not_a_license = int(url in [
        "https://creativecommons.org/public-domain/",
        "http://creativecommons.org/licenses/publicdomain/",
        "https://creativecommons.org/licenses/publicdomain/",
    ])
    # 1. Priority order in LICENSES_BY_TYPE
    type_priority = float('inf')
    for idx, urls in enumerate(LICENSES_BY_TYPE.values()):
        if url in urls:
            type_priority = idx
            break
    # 2. Contains 'license' or 'licensing'
    contains_license = int(bool(re.search(r'license|licensing', url, re.I)))
    # 3. Contains 'terms'
    contains_terms = int('terms' in url.lower())
    # 4. Contains 'stock.adobe.com' or 'vectorstock'
    contains_stock = int('stock.adobe.com' in url.lower() or 'vectorstock' in url.lower())
    # Sorting: lower is higher priority (→ negative for booleans)
    return (
        not_a_license,
        type_priority,
        -contains_license,
        -contains_terms,
        -contains_stock,
        url
    )

def sort_license_urls(database, mock: bool = False):
    with database.session_scope() as session:
        # Find all licenses with Creative Commons URLs that aren't already approved
        statement = select(License).where(func.json_array_length(License.urls) > 1)
        licenses = session.exec(statement).all()

        updated_count = 0
        for license in licenses:
            old_license_urls = license.urls
            license.urls.sort(key=license_url_sort_key)
            if old_license_urls != license.urls:
                print(f"Sorted license URLs for license {license.id}: {old_license_urls} -> {license.urls}")
            else:
                if not mock:
                    print(f"License URLs already sorted for license {license.id}: {license.urls}")
            if not mock:
                session.add(license)
            updated_count += 1

        print(f"Sorted license URLs for {updated_count} licenses")


