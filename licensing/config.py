from licensing.config_model import Model

class Configuration(Model):
    @classmethod
    def load(cls, path="config.json"):
        with open(path, "r") as f:
            return cls.model_validate_json(f.read())
