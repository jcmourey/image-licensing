from sqlmodel import func, select, case, or_

from backend.google_apis.vision import Vision
from backend.model.image import Image
from backend.model.license import License
from backend.model.match import Match


def update_images(database, max_search_results: int):
    vision = Vision(publish=database.save_unique_matches)

    with database.session_scope() as session:
        results = get_images_and_match_count(session, max_search_results)
        # results = results[3:4]
        print(f"Updating {len(results)} images")
        vision.batch_search(results, max_search_results)


def get_images_and_match_count(session, max_search_results: int):
    match_count = func.count(Match.id)

    # Create a CASE expression for the HAVING clause to properly count approved licenses
    approved_license_count = func.sum(
        case(
            (License.approved == True, 1),
            else_=0
        )
    )

    stmt = (
        select(
            Image,
            func.coalesce(Image.web_entities_found, match_count).label("match_count")
        )
        # Fix the WHERE clause to use SQLAlchemy operators
        .where(
            or_(
                Image.web_entities_requested.is_(None),
                Image.web_entities_found.is_(None),
                Image.web_entities_found >= Image.web_entities_requested
            )
        )
        .where(
            or_(
                Image.web_entities_requested.is_(None),
        Image.web_entities_requested < max_search_results
            )
        )
        .outerjoin(License, License.parent_image_id == Image.id)
        .outerjoin(Match, Match.parent_image_id == Image.id)
        .group_by(Image.id)
        # Fix the HAVING clause to use the case expression
        .having(approved_license_count == 0)
        .order_by("match_count")
    )

    return session.exec(stmt).all()


