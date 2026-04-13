import logging
import os.path
from typing import Any, Dict

class ApplicationExternalConfig:
    """
    Represents the external configuration of the application
    supplied by the user via .json file
    """

    PROJECT_PROPERTY = "project"
    PROJECT_ABBR_PROPERTY = "PROJECT_ABBR"

    UI_PROPERTY = "ui"
    UI_VERSION_PROPERTY = "VERSION"
    UI_TITLE_PROPERTY = "TITLE"

    DANGEROUS_PROPERTY = "dangerous"
    DANGEROUS_GAMS3_PRODUCTION_ORIGIN_PROPERTY = "GAMS3_PRODUCTION_ORIGIN"
    DANGEROUS_GAMS5_PRODUCTION_ORIGIN_PROPERTY = "GAMS5_PRODUCTION_ORIGIN"

    MODE_LOAD_PROPERTY = "load"
    MODE_GAMS_API_ORIGIN_PROPERTY = "GAMS_API_ORIGIN"
    MODE_IIIF_IMAGE_SERVER_PROPERTY = "IIIF_IMAGE_SERVER_ORIGIN"
    MODE_OUTPUT_PATH_PROPERTY = "OUTPUT_PATH"

    MODE_LOAD_OBJECT_COUNT_RESTRICTION = "OBJECT_COUNT_RESTRICTION"
    MODE_LOAD_OBJECTS_REQUIRED = "OBJECTS_REQUIRED"


    config: Dict[str, Any]
    """
    The configuration dictionary (usually extracted from json file)
    """

    def __init__(self, config: Dict[str, Any], mode: str):
        self.config = config
        self.mode = mode


    def get(self, key: str):
        """
        Returns the value of the key in the configuration
        :param key: the key to get the value for
        :return: the value of the key
        """
        if key not in self.config:
            raise ValueError(f"Cannot find required property {key} in config file")

        return self.config[key]

    def get_obj_count_restriction(self) -> int | None:
        """
        Returns the object count restriction
        :return: the object count restriction
        """
        sub_dict: Dict[Any] = self.get(self.mode).get(self.MODE_LOAD_PROPERTY)
        if sub_dict is None:
            logging.debug(f"No {self.mode}.{self.MODE_LOAD_PROPERTY} property found in config file. No object count restriction defined.")
            return None

        if self.MODE_LOAD_OBJECT_COUNT_RESTRICTION not in sub_dict:
            logging.debug(f"No {self.mode}.{self.MODE_LOAD_PROPERTY}.{self.MODE_LOAD_OBJECT_COUNT_RESTRICTION} property found in config file. No object count restriction defined.")
            return None

        extracted_value = sub_dict.get(self.MODE_LOAD_OBJECT_COUNT_RESTRICTION)

        if not isinstance(extracted_value, int):
            raise ValueError(f"Expected {self.mode}.{self.MODE_LOAD_PROPERTY}.{self.MODE_LOAD_OBJECT_COUNT_RESTRICTION} to be an integer, but got '{sub_dict.get('objectCountRestriction')}'")

        return int(extracted_value)


    def get_obj_required(self) -> list[str]:
        """
        Returns the objects required: List of strings (object ids)
        :return: the objects required to be loaded. Empty list if not defined or property is empty.
        """
        sub_dict: Dict[Any] = self.get(self.mode).get(self.MODE_LOAD_PROPERTY)
        if sub_dict is None:
            logging.debug(f"No {self.mode}.{self.MODE_LOAD_PROPERTY} property found in config file. No required objects defined.")
            return []

        if self.MODE_LOAD_OBJECTS_REQUIRED not in sub_dict:
            logging.debug(f"No {self.mode}.{self.MODE_LOAD_PROPERTY}.{self.MODE_LOAD_OBJECTS_REQUIRED} property found in config file. No required objects defined.")
            return []

        return sub_dict.get(self.MODE_LOAD_OBJECTS_REQUIRED)

    def get_gams3_production_origin(self) -> str:
        """
        Returns the configured origin of gams3
        :return: the configured origin of gams3
        """
        sub_dict: Dict[Any] = self.get(self.DANGEROUS_PROPERTY)
        if sub_dict is None:
            raise ValueError(f"No {self.DANGEROUS_PROPERTY} property found in config file. No required objects defined.")

        if self.DANGEROUS_GAMS3_PRODUCTION_ORIGIN_PROPERTY not in sub_dict:
            raise ValueError(f"No {self.DANGEROUS_PROPERTY}.{self.DANGEROUS_GAMS3_PRODUCTION_ORIGIN_PROPERTY} property found")

        return sub_dict.get(self.DANGEROUS_GAMS3_PRODUCTION_ORIGIN_PROPERTY)

    def get_gams5_production_origin(self) -> str:
        """
        Returns the configured origin of gams3
        :return: the configured origin of gams3
        """
        sub_dict: Dict[Any] = self.get(self.DANGEROUS_PROPERTY)
        if sub_dict is None:
            raise ValueError(f"No {self.DANGEROUS_PROPERTY} property found in config file. No required objects defined.")

        if self.DANGEROUS_GAMS5_PRODUCTION_ORIGIN_PROPERTY not in sub_dict:
            raise ValueError(f"No {self.DANGEROUS_PROPERTY}.{self.DANGEROUS_GAMS5_PRODUCTION_ORIGIN_PROPERTY} property found")

        return sub_dict.get(self.DANGEROUS_GAMS5_PRODUCTION_ORIGIN_PROPERTY)


    def get_gams_api_origin(self) -> str:
        """
        Returns the GAMS API origin URL
        :return: the GAMS API origin URL
        """
        configured_origin = self.get(self.mode).get(self.MODE_GAMS_API_ORIGIN_PROPERTY)
        if configured_origin is None:
            raise ValueError(f"Cannot find (or empty) required property {self.mode}.{self.MODE_GAMS_API_ORIGIN_PROPERTY} in config file")

        if not configured_origin.startswith("http"):
            raise ValueError(f"Expected {self.mode}.{self.MODE_GAMS_API_ORIGIN_PROPERTY} to be a valid URL starting with 'http', but got '{configured_origin}'")

        if configured_origin.endswith("/"):
            raise ValueError(f"Expected {self.mode}.{self.MODE_GAMS_API_ORIGIN_PROPERTY} to not have a trailing slash, but got '{configured_origin}'")

        return configured_origin

    def get_iiif_image_server_origin(self) -> str:
        """
        Returns the configured IIIF image server url
        """
        configured_origin = self.get(self.mode).get(self.MODE_IIIF_IMAGE_SERVER_PROPERTY)
        if configured_origin is None:
            raise ValueError(f"Cannot find (or empty) required property {self.mode}.{self.MODE_IIIF_IMAGE_SERVER_PROPERTY} in config file")

        if not configured_origin.startswith("http"):
            raise ValueError(f"Expected {self.mode}.{self.MODE_IIIF_IMAGE_SERVER_PROPERTY} to be a valid URL starting with 'http', but got '{configured_origin}'")

        if configured_origin.endswith("/"):
            raise ValueError(f"Expected {self.mode}.{self.MODE_IIIF_IMAGE_SERVER_PROPERTY} to not have a trailing slash, but got '{configured_origin}'")

        return configured_origin


    def get_project_abbr(self) -> str:
        """
        Returns the project abbreviation
        :return: the project abbreviation
        """
        return self.get(self.PROJECT_PROPERTY).get(self.PROJECT_ABBR_PROPERTY)


    def get_output_path(self) -> str | None:
        """
        Returns the output path from the configuration
        :return: the output path
        """
        configured_path = self.get(self.mode).get(self.MODE_OUTPUT_PATH_PROPERTY)
        if configured_path is None:
            return None

        # validate path
        if not isinstance(configured_path, str):
            raise ValueError(f"Expected {self.mode}.{self.MODE_OUTPUT_PATH_PROPERTY} to be a string, but got '{configured_path}'")

        if not os.path.isabs(configured_path):
            raise ValueError(f"Expected {self.mode}.{self.MODE_OUTPUT_PATH_PROPERTY} to be an absolute path, but got '{configured_path}'")

        logging.info(f"*** Found configured {self.MODE_OUTPUT_PATH_PROPERTY} in configuration file. Using now: '{configured_path}'")
        return configured_path

    def get_ui_version(self) -> str | None:
        """
        Returns the UI version from the configuration
        """
        ui_dict: Dict[Any] = self.get(self.UI_PROPERTY)
        if ui_dict is None:
            return None

        configured_version = ui_dict.get(self.UI_VERSION_PROPERTY)
        if configured_version is None:
            return None

        if not isinstance(configured_version, str):
            raise ValueError(f"Expected {self.UI_PROPERTY}.{self.UI_VERSION_PROPERTY} to be a string, but got '{configured_version}'")

        if len(configured_version) == 0:
            raise ValueError(f"Expected {self.UI_PROPERTY}.{self.UI_VERSION_PROPERTY} to be a non-empty string, but got an empty string")

        if len(configured_version.split(".")) < 2:
            raise ValueError(f"Expected {self.UI_PROPERTY}.{self.UI_VERSION_PROPERTY} to be a semantic version string, but got '{configured_version}'")

        return configured_version


    def get_ui(self) -> Dict[str, Any] | None:
        """
        Returns the UI configuration dictionary
        """
        ui_dict: Dict[str, Any] = self.get(self.UI_PROPERTY)
        if ui_dict is None:
            return None

        return ui_dict

    def get_ui_title(self) -> str | None:
        """
        Returns the UI title from the configuration
        """
        ui_dict: Dict[Any] = self.get(self.UI_PROPERTY)
        if ui_dict is None:
            return None

        configured_title = ui_dict.get(self.UI_TITLE_PROPERTY)
        if configured_title is None:
            return None

        return configured_title