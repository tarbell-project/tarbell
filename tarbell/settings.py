# -*- coding: utf-8 -*-
import os
import sys
import yaml

from clint.textui import colored
from .utils import show_error

EMPTY_BLUEPRINT = {"name": "Empty project (no blueprint)"}

class Settings:
    """Simple object representation of Tarbell settings."""
    def __init__(self, path):
        self.path = path

        self.config = {}
        try:
            with open(self.path) as f:
                self.config = yaml.load(f)
        except IOError:
            show_error("No Tarbell configuration found, please run `{0}`."
                       .format(colored.yellow('tarbell configure')))

        self.config["project_templates"] = self.config.get("project_templates", [])
        self.config["project_templates"].append(EMPTY_BLUEPRINT)

        self.client_secrets = False
        client_secrets_path = os.path.join(os.path.dirname(self.path), "client_secrets.json")

        try:
            with open(client_secrets_path) as f:
                self.client_secrets = True
        except IOError:
            pass

    def save(self):
        with open(self.path, "w") as f:
            self.config["project_templates"].pop()
            yaml.dump(self.config, f, default_flow_style=False)
