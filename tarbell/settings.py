import yaml
import os

class Settings:
    """Simple object representation of Tarbell settings."""
    def __init__(self, path):
        self.path = path

        self.config = {}
        config_path = os.path.join(self.path, "settings.yaml")
        with open(config_path) as f:
            self.config = yaml.load(f)

        self.client_secrets = False
        client_secrets_path = os.path.join(self.path, "client_secrets.json")
        with open(client_secrets_path) as f:
            self.client_secrets = True
