
from typing import Any, Dict

class ApplicationExternalConfig:
    """
    Represents the external configuration of the application
    supplied by the user via .json file
    """

    PROJECT_PROPERTY = "project"
    PROJECT_ABBR_PROPERTY = "projectAbbr"

    DEVELOP_PROPERTY = "develop"
    PRODUCTION_PROPERTY = "production"

    MODE_GAMS_API_ORIGIN_PROPERTY = "gamsApiOrigin"
    MODE_OUTPUT_PATH_PROPERTY = "outputPath"

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
            return None

        return self.config[key]

    def get_obj_count_restriction(self):
        """
        Returns the object count restriction
        :return: the object count restriction
        """
        sub_dict: Dict[Any] = self.get(self.mode).get("load")
        if sub_dict is None:
            return None

        return sub_dict.get("objectCountRestriction")


    def get_obj_required(self):
        """
        Returns the objects required: List of strings (object ids)
        :return: the objects required to be loaded
        """
        sub_dict: Dict[Any] = self.get(self.mode).get("load")
        if sub_dict is None:
            return None

        return sub_dict.get("objectsRequired")

    def get_gams_api_origin(self) -> str:
        """
        Returns the GAMS API origin URL
        :return: the GAMS API origin URL
        """
        return self.get(self.mode).get(self.MODE_GAMS_API_ORIGIN_PROPERTY)


    def get_project_abbr(self) -> str:
        """
        Returns the project abbreviation
        :return: the project abbreviation
        """
        return self.get(self.PROJECT_PROPERTY).get(self.PROJECT_ABBR_PROPERTY)