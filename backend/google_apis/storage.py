from google.cloud import storage
from .credentials import get_creds

class Storage:
    def __init__(self, project_name, bucket_name):
        self.project_name = project_name
        self.bucket_name = bucket_name

        self.creds = get_creds()
        self.client = storage.Client(credentials=self.creds, project=self.project_name)
        self.bucket = self.client.bucket(self.bucket_name)
   	
    @property
    def blobs(self):
        return [blob for blob in self.bucket.list_blobs()]

    @property
    def blobs_by_id(self):
        return {blob.id: blob for blob in self.blobs}

    def download_to_memory(self, blob_name):
        blob = self.bucket.blob(blob_name)
        return blob.download_as_bytes()

