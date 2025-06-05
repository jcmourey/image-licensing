class ImageSet:
    def __init__(self, storage, database, thumbnail_service, max_matches):
        self.storage = storage
        self.database = database
        self.max_matches = max_matches
        self.thumbnail_service = thumbnail_service


    # ---- REFACTOR ---
    @property
    def is_complete(self):
        return not self.eligible_images
        
    @property
    def incomplete_licens(self):
        return [i for i in self.images if i.is_eligible_to_get_more_matches(self.max_matches)]


