import json
import os

from pollin.System.init.ApplicationContext import ApplicationContext
from typing import Dict, Any

class ApplicationExternalConfigImporter:
    """
    Imports the project configuration file from defined location at init process

    """
    app_context: ApplicationContext

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context

    def config_file_exists(self):
        """
        Checks if the project configuration file exists
        :return: True if the config file exists, False otherwise
        """
        path = self.app_context.get_config().project_config_json
        return os.path.exists(path)

    def import_config(self):
        """
        Imports the project configuration file from defined location at init process.
        :return: configuration dictionary as json
        """

        if not self.config_file_exists():
            return None

        config_json_path = self.app_context.get_config().project_config_json

        # TODO think about errors
        # load json as dictionary
        with open(config_json_path, 'r') as f:
            config_json_dict: Dict[str, Any] = json.load(f)
            return config_json_dict
