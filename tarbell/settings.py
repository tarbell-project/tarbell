# -*- coding: utf-8 -*-
import yaml
import os
from clint.textui import colored, puts


class Settings:
    """Simple object representation of Tarbell settings."""
    def __init__(self, path):
        self.path = path

        self.config = {}
        try:
            with open(self.path) as f:
                self.config = yaml.load(f)
        except IOError:
            puts("{0}: {1}".format(
                colored.red("Warning:"),
                "No Tarbell configuration found, please run `tarbell configure`."
            ))

        self.client_secrets = False
        client_secrets_path = os.path.join(os.path.dirname(self.path), "client_secrets.json")
        try:
            with open(client_secrets_path) as f:
                self.client_secrets = True
        except IOError:
            pass

    def save(self):
        with open(self.path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)
