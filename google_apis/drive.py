from .credentials import get_drive_service

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