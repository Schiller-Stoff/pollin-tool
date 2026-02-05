import logging
import os
import tomllib
from os import PathLike
from pathlib import Path
from typing import Dict, Any

from pollin.init.config.ApplicationConfiguration import ApplicationConfiguration
from pollin.init.config.ApplicationExternalConfig import ApplicationExternalConfig


class ApplicationExternalConfigImporter:
    """
    Imports the project configuration file from defined location at init process

    """

    @staticmethod
    def _deep_merge(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merges the overrides dictionary into the base dictionary.
        """
        for key, value in overrides.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                ApplicationExternalConfigImporter._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

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

        config_path = Path(config_file_path_str)

        if not config_path.exists():
            msg = f"Cannot find required configuration file {ApplicationConfiguration.CONFIG_FILE_NAME} at expected path: {config_path}"
            raise FileNotFoundError(msg)

        # 1. Load Base Config (pollin.toml)
        with open(config_path, 'rb') as f:
            config_toml_dict: Dict[str, Any] = tomllib.load(f)

        # 2. Look for Override Config (pollin.local.toml)
        # We assume it sits right next to the main config file
        local_config_path = config_path.parent / "pollin.override.toml"

        if local_config_path.exists() and local_config_path.is_file():
            logging.info(f"Found local override configuration: {local_config_path}")
            try:
                with open(local_config_path, 'rb') as f:
                    local_overrides = tomllib.load(f)
                    config_toml_dict = ApplicationExternalConfigImporter._deep_merge(config_toml_dict, local_overrides)
            except Exception as e:
                logging.warning(f"Failed to load or merge local configuration file: {e}")

        # 3. Validation (performed on the merged result)
        cur_mode = mode

        if ApplicationExternalConfig.PROJECT_PROPERTY not in config_toml_dict:
            raise ValueError(f"'{ApplicationExternalConfig.PROJECT_PROPERTY}' property not found...")

        # toml validation
        if ApplicationExternalConfig.PROJECT_PROPERTY not in config_toml_dict:
            raise ValueError(f"'{ApplicationExternalConfig.PROJECT_PROPERTY}' property not found (or empty) in the configuration.")
        else:
            if not config_toml_dict.get(ApplicationExternalConfig.PROJECT_PROPERTY).get(ApplicationExternalConfig.PROJECT_ABBR_PROPERTY):
                raise ValueError(f"'{ApplicationExternalConfig.PROJECT_PROPERTY}.{ApplicationExternalConfig.PROJECT_ABBR_PROPERTY}' not found (or empty) in configuration")

        if not config_toml_dict.get(cur_mode):
            raise ValueError(f"For the currently active mode: '{cur_mode}' is no (or empty) toml property '{cur_mode}' defined. In config.")

        if not config_toml_dict.get(cur_mode).get(ApplicationExternalConfig.MODE_GAMS_ORIGIN):
            raise ValueError(f"Cannot find (or empty) required property {cur_mode}.{ApplicationExternalConfig.MODE_GAMS_ORIGIN} in config")

        if not config_toml_dict.get(cur_mode).get(ApplicationExternalConfig.MODE_GAMS_API_ORIGIN_PROPERTY):
            raise ValueError(f"Cannot find (or empty) required property {cur_mode}.{ApplicationExternalConfig.MODE_GAMS_API_ORIGIN_PROPERTY} in config")

        if not config_toml_dict.get(ApplicationExternalConfig.UI_PROPERTY):
            raise ValueError(f"Cannot find (or empty) required property {ApplicationExternalConfig.UI_PROPERTY} in config")

        if not config_toml_dict.get(ApplicationExternalConfig.UI_PROPERTY).get(ApplicationExternalConfig.UI_VERSION_PROPERTY):
            raise ValueError(f"Cannot find (or empty) required property {ApplicationExternalConfig.UI_PROPERTY}.{ApplicationExternalConfig.UI_VERSION_PROPERTY} in config")

        return config_toml_dict
