from sqlalchemy import func
from sqlmodel import select
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


def update_approved_licenses(database):
    with database.session_scope() as session:
        # Find all licenses with Creative Commons URLs that aren't already approved
        statement = select(License).where(
            License.approved == False
        )
        licenses = session.exec(statement).all()

        updated_count = 0
        for license in licenses:
            if license.is_approved:
                license.approved = True
                session.add(license)
                updated_count += 1

        print(f"Updated 'approved' flag for {updated_count} licenses")

