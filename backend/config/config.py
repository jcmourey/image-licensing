from backend.constants import CONFIG_PATH
from backend.config.generated_config_model import Model

class Configuration(Model):
    @classmethod
    def load(cls, path=CONFIG_PATH):
        with open(path, "r") as f:
            return cls.model_validate_json(f.read())
