import os
import tomllib

from pollin.System.init.ApplicationContext import ApplicationContext
from typing import Dict, Any

from pollin.System.init.ApplicationExternalConfig import ApplicationExternalConfig


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
        path = self.app_context.get_config().project_config_toml
        return os.path.exists(path)

    def import_config(self):
        """
        Imports the project configuration file from defined location at init process.
        :return: configuration dictionary from toml
        """

        if not self.config_file_exists():
            return None

        config_toml_path = self.app_context.get_config().project_config_toml

        # load toml as dictionary
        with open(config_toml_path, 'rb') as f:
            config_toml_dict: Dict[str, Any] = tomllib.load(f)
            cur_mode = self.app_context.get_config().mode

            # toml validation

            # if ApplicationExternalConfig.PROJECT_PROPERTY not in config_toml_dict:
            #     raise ValueError(f"'{ApplicationExternalConfig.PROJECT_PROPERTY}' property not found (or empty) in the configuration file: {config_toml_path}")
            # else:
            #     if not config_toml_dict.get(ApplicationExternalConfig.PROJECT_PROPERTY).get(ApplicationExternalConfig.PROJECT_ABBR_PROPERTY):
            #         raise ValueError(f"'{ApplicationExternalConfig.PROJECT_PROPERTY}.{ApplicationExternalConfig.PROJECT_ABBR_PROPERTY}' not found (or empty) in configuration file: {config_toml_path}")

            if not config_toml_dict.get(cur_mode):
                raise ValueError(f"For the currently active mode: '{cur_mode}' is no (or empty) toml property '{cur_mode}' defined. In config toml file: {config_toml_path} ")

            # if not config_toml_dict.get(cur_mode).get(ApplicationExternalConfig.MODE_BASE_PROPERTY):
            #     raise ValueError(f"Cannot find (or empty) required property {cur_mode}.{ApplicationExternalConfig.MODE_BASE_PROPERTY} in config toml file: {config_toml_path}")
            #
            # if not config_toml_dict.get(cur_mode).get(ApplicationExternalConfig.MODE_BASE_PROPERTY).get(ApplicationExternalConfig.MODE_BASE_GAMS_API_HOST_PROPERTY):
            #     raise ValueError(f"Cannot find (or empty) required property {cur_mode}.{ApplicationExternalConfig.MODE_BASE_GAMS_API_HOST_PROPERTY} in config toml file: {config_toml_path}")
            #
            # if not config_toml_dict.get(cur_mode).get(ApplicationExternalConfig.MODE_BASE_PROPERTY).get(ApplicationExternalConfig.MODE_BASE_OUTPUT_PATH_PROPERTY):
            #     raise ValueError(f"Cannot find (or empty) required property {cur_mode}.{ApplicationExternalConfig.MODE_BASE_OUTPUT_PATH_PROPERTY} in config toml file: {config_toml_path}")
            #
            # if not config_toml_dict.get(cur_mode).get(ApplicationExternalConfig.MODE_BASE_PROPERTY).get(ApplicationExternalConfig.MODE_BASE_SRC_PATH_PROPERTY):
            #     raise ValueError(f"Cannot find (or empty) required property {cur_mode}.{ApplicationExternalConfig.MODE_BASE_SRC_PATH_PROPERTY} in config toml file: {config_toml_path}")


            # TODO return complete config file not only mode dictionary

            # default to empty dict if mode not found
            return config_toml_dict.get(cur_mode, {})
