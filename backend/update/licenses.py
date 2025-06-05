from sqlmodel import select
from backend.model.match import Match
from backend.model.license import License


def update_licenses(database):
    with database.session_scope() as session:
        # Match.page_url == Match.image_url means Google Vision didn't return a page for the image
        # TODO figure out a better way to do this (find the license from the root page)
        statement = select(Match).where((None == Match.license) & (Match.page_url != Match.image_url))
        matches = session.exec(statement).all()
        print(f"Updating licenses for {len(matches)} matches")
        for match in matches:
            new_license = License.extract_page_license_metadata(match)
            if new_license is not None:
                session.add(new_license)
                session.commit()