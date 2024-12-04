
from typing import Any, Dict

class ApplicationExternalConfig:
    """
    Represents the external configuration of the application
    supplied by the user via .json file
    """

    config: Dict[str, Any]
    """
    The configuration dictionary (usually extracted from json file)
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config


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
        sub_dict: Dict[Any] = self.get("load")
        if sub_dict is None:
            return None

        return sub_dict.get("objectCountRestriction")


    def get_obj_required(self):
        """
        Returns the objects required: List of strings (object ids)
        :return: the objects required to be loaded
        """
        sub_dict: Dict[Any] = self.get("load")
        if sub_dict is None:
            return None

        return sub_dict.get("objectsRequired")
