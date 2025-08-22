import os
import tomllib
from os import PathLike
from typing import Dict, Any

from pollin.System.init.config.ApplicationExternalConfig import ApplicationExternalConfig


class ApplicationExternalConfigImporter:
    """
    Imports the project configuration file from defined location at init process

    """

    @staticmethod
    def config_file_exists(config_file_path_str: PathLike) -> bool:
        """
        Checks if the project configuration file exists
        :return: True if the config file exists, False otherwise
        """
        return os.path.exists(config_file_path_str) and os.path.isfile(config_file_path_str)


    @staticmethod
    def import_config(config_file_path_str: PathLike, mode: str):
        """
        Imports the project configuration file from defined location at init process.
        :return: configuration dictionary from toml
        """

        if not ApplicationExternalConfigImporter.config_file_exists(config_file_path_str):
            return None

        config_toml_path = config_file_path_str

        # load toml as dictionary
        with open(config_toml_path, 'rb') as f:
            config_toml_dict: Dict[str, Any] = tomllib.load(f)
            cur_mode = mode

            # toml validation
            if ApplicationExternalConfig.PROJECT_PROPERTY not in config_toml_dict:
                raise ValueError(f"'{ApplicationExternalConfig.PROJECT_PROPERTY}' property not found (or empty) in the configuration file: {config_toml_path}")
            else:
                if not config_toml_dict.get(ApplicationExternalConfig.PROJECT_PROPERTY).get(ApplicationExternalConfig.PROJECT_ABBR_PROPERTY):
                    raise ValueError(f"'{ApplicationExternalConfig.PROJECT_PROPERTY}.{ApplicationExternalConfig.PROJECT_ABBR_PROPERTY}' not found (or empty) in configuration file: {config_toml_path}")

            if not config_toml_dict.get(cur_mode):
                raise ValueError(f"For the currently active mode: '{cur_mode}' is no (or empty) toml property '{cur_mode}' defined. In config toml file: {config_toml_path} ")

            if not config_toml_dict.get(cur_mode).get(ApplicationExternalConfig.MODE_GAMS_API_ORIGIN_PROPERTY):
                raise ValueError(f"Cannot find (or empty) required property {cur_mode}.{ApplicationExternalConfig.MODE_GAMS_API_ORIGIN_PROPERTY} in config toml file: {config_toml_path}")

            if not config_toml_dict.get(ApplicationExternalConfig.UI_PROPERTY):
                raise ValueError(f"Cannot find (or empty) required property {cur_mode}.{ApplicationExternalConfig.UI_PROPERTY} in config toml file: {config_toml_path}")

            if not config_toml_dict.get(ApplicationExternalConfig.UI_PROPERTY).get(ApplicationExternalConfig.UI_VERSION_PROPERTY):
                raise ValueError(f"Cannot find (or empty) required property {cur_mode}.{ApplicationExternalConfig.UI_PROPERTY}.{ApplicationExternalConfig.UI_VERSION_PROPERTY} in config toml file: {config_toml_path}")

            return config_toml_dict
