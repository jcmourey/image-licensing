from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload, MediaFileUpload
import os
from .credentials import get_creds


def get_drive_service():
    creds = get_creds()
    service = build("drive", "v3", credentials=creds)
    return creds, service


def get_or_create_subfolder(service, parent_folder_id, subfolder_name):
    # Search for the subfolder
    query = (
        f"'{parent_folder_id}' in parents and "
        f"name = '{subfolder_name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    response = service.files().list(q=query, fields="files(id,name)").execute()
    files = response.get('files', [])
    if files:
        return files[0]['id']
    # Create the subfolder
    file_metadata = {
        'name': subfolder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')

def upload_html_and_thumbs_to_drive(html, folder_id, thumb_paths):
    import os
    creds, service = get_drive_service()

    # 1. Upload HTML file (to main folder)
    file_metadata = {
        'name': 'attributions.html',
        'parents': [folder_id],
        'mimeType': 'text/html',
    }
    media = MediaInMemoryUpload(html.encode('utf-8'), mimetype="text/html")
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webViewLink'
    ).execute()

    # Make the HTML file public
    service.permissions().create(
        fileId=file['id'],
        body={"type": "anyone", "role": "reader"},
    ).execute()
    print(f"Attributions file URL: {file.get('webViewLink')}")

    # 2. Get or create thumbnails subfolder
    thumbnails_folder_id = get_or_create_subfolder(service, folder_id, "thumbnails")

    # 3. Upload thumbnails to the thumbnails subfolder
    thumb_urls = []
    for thumb_path in thumb_paths:
        thumb_name = os.path.basename(thumb_path)
        thumb_metadata = {
            'name': thumb_name,
            'parents': [thumbnails_folder_id],
            'mimeType': 'image/jpeg'
        }
        media = MediaFileUpload(thumb_path, mimetype='image/jpeg')
        thumb_file = service.files().create(
            body=thumb_metadata,
            media_body=media,
            fields='id'
        ).execute()

        # Make thumbnail public
        service.permissions().create(
            fileId=thumb_file['id'],
            body={"type": "anyone", "role": "reader"},
        ).execute()

        # Get direct view URL for <img src="">
        direct_url = f"https://drive.google.com/uc?id={thumb_file['id']}"
        thumb_urls.append(direct_url)
        print(f"Thumbnail uploaded: {direct_url}")

    return file, thumb_urls


def upload_html_to_drive(html, folder_id):
    creds, service = get_drive_service()
    file_metadata = {
        'name': 'attributions.html',
        'parents': [folder_id],
        'mimeType': 'text/html',
    }
    media = MediaInMemoryUpload(html.encode('utf-8'), mimetype="text/html")

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webViewLink'
    ).execute()

    # Make the file "anyone with the link can view"
    service.permissions().create(
        fileId=file['id'],
        body={"type": "anyone", "role": "reader"},
    ).execute()

    print(f"Attributions file URL: {file.get('webViewLink')}")
    return file


def get_folder_id_by_path(service, parent_id, path):
    """
    Given a starting parent folder_id and a subdirectory path like 'foo/bar/baz',
    finds the folder_id for the final subfolder.
    """
    if not path:
        return parent_id
    parts = [p for p in path.strip('/').split('/') if p]
    current_id = parent_id
    for part in parts:
        query = (
            f"'{current_id}' in parents and name = '{part}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            pageSize=10,
        ).execute()
        files = results.get("files", [])
        if not files:
            raise FileNotFoundError(f"Subdirectory '{part}' not found in parent {current_id}")
        current_id = files[0]["id"]
    return current_id


def list_files_in_folder(folder_id, subdirectory=None):
    creds, service = get_drive_service()

    if subdirectory is not None:
        folder_id = get_folder_id_by_path(service, folder_id, subdirectory)

    files = []
    page_token = None
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            pageSize=1000,
        ).execute()
        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break
    return files

def file_url(item):
    return f"https://drive.usercontent.google.com/uc?export=download&id={item['id']}"

def file_name(item):
    return item['name']