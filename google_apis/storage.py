from google.cloud import storage
from .credentials import get_creds


def get_bucket_blobs(bucket_name, project_name):
    creds = get_creds()
    client = storage.Client(credentials=creds, project=project_name)
    bucket = client.bucket(bucket_name)
    return [blob for blob in bucket.list_blobs()]


def get_gcs_uri(blob):
    return f"gs://{blob.bucket.name}/{blob.name}"
