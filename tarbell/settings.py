# -*- coding: utf-8 -*-
import os
import sys
import yaml

from clint.textui import colored
from .utils import show_error

EMPTY_BLUEPRINT = {"name": "Empty project (no blueprint)"}

class Settings:
    """
    Simple object representation of Tarbell settings.
    """
    def __init__(self):
        self.path = os.path.expanduser(
            os.path.join("~", ".tarbell", "settings.yaml")
        )

        self.config = {}
        try:
            with open(self.path) as f:
                self.config = yaml.load(f)
                self.file_missing = False
        except IOError:
            self.file_missing = True

        self.config["project_templates"] = self.config.get("project_templates", [])
        self.config["project_templates"].append(EMPTY_BLUEPRINT)
        self.config["default_server_ip"] = self.config.get("default_server_ip", "127.0.0.1")
        self.config["default_server_port"] = self.config.get("default_server_port", "5000")

        client_secrets_path = os.path.join(os.path.dirname(self.path), "client_secrets.json")
        try:
            with open(client_secrets_path) as f:
                self.client_secrets = True
                self.client_secrets_path = client_secrets_path
        except IOError:
            self.client_secrets = False

        credentials_path = os.path.join(os.path.dirname(self.path), "credentials.json")
        try:
            with open(credentials_path) as f:
                self.credentials = True
                self.credentials_path = credentials_path
        except IOError:
            self.credentials = False

    def save(self):
        """
        Save settings.
        """
        with open(self.path, "w") as f:
            self.config["project_templates"] = list(filter(lambda template: template.get("url"), self.config["project_templates"]))
            yaml.dump(self.config, f, default_flow_style=False)
