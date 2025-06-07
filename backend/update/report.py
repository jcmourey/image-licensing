from sqlmodel import select
from backend.model.image import Image


def report(database):
    with database.session_scope() as session:
        statement = select(Image)
        images = session.exec(statement).all()
        image_count = len(images)
        license_count = sum(
            any(match.license and (match.license.meta_info or match.license.urls) for match in image.matches)
            for image in images
        )
        url_count = sum(
            any(match.license and match.license.urls for match in image.matches)
            for image in images
        )
        print("\nREPORT")
        print(f"Image count: {image_count}")
        print(f"License count: {license_count}")
        print(f"URL count: {url_count}")

        sorted_images = sorted(
            images,
            key=lambda i: (
                not any(match.license and match.license.urls for match in i.matches),  # False (has url) comes before True (no url)
                -len(i.matches)  # more matches first
            )
        )

        for image in sorted_images:
            match_count = len(image.matches)
            license_count = sum(bool(match.license and (match.license.meta_info or match.license.urls)) for match in image.matches)
            url_count = sum(bool(match.license and match.license.urls) for match in image.matches)
            print(f"{match_count} matches, {license_count} licenses, {url_count} url for: '{image.name}'")

        images_with_url = [
            (image, match.license.urls[0])
            for image in images
            for match in image.matches
            if match.license and match.license.urls
               # Only take the first matching match per image:
               and not any(
                prev_match.license and prev_match.license.urls
                for prev_match in image.matches[:image.matches.index(match)]
            )
        ]
        print(f"Images with URL:")
        for image, url in images_with_url:
            print(f"  {image.name}: {url}")

        # Count total matches
        total_matches = sum(len(image.matches) for image in images)

        # Calculate cost (per 1000 matches)
        cost_per_1000 = 3.50
        cost = (total_matches / 1000) * cost_per_1000

        print("")
        print(f"Total matches: {total_matches}")
        print(f"Cost at 3.50€ per 1000: {cost:.2f}€")