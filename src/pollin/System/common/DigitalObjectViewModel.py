from typing import List, Dict

class DigitalObjectViewModel:
    """
    Model class for the views rendered by jinja2 templates
    """

    dc: dict[str, List[str]]
    """
    Dublin Core metadata of the object
    """

    db: dict[str, str]
    """
    Object metadata from the database
    """

    props: dict[str, any]
    """
    Search json properties of the object
    """

    component_map: Dict[str, str]
    """
    Web component representation of the .xml datastreams of the object.
    """

    def __init__(self, dc: dict[str, any], db: dict[str, any], props: dict[str, any], component_map: Dict[str, str] = None):
        self.dc = dc
        self.db = db
        self.props = props
        if component_map is None:
            self.component_map = {}
        else:
            self.component_map = component_map

    def to_dict(self):
        """
        Converts the object to a dictionary
        :return: dictionary representation of the object
        """
        return {
            "dc": self.dc,
            "db": self.db,
            "props": self.props
        }
