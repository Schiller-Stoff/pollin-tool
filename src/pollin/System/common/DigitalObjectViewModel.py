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

    def to_geo_point_feature(self):
        """
        Converts the object to a geo point feature
        :return: geo point feature dictionary representation of the object or None if no geo data is available
        """

        if not self.props:
            return None

        # TODO handle via constants - GAMS5 specific
        object_long_lat: str = self.props.get("entityLongLat")
        if not object_long_lat:
            return None


        object_long_lat = object_long_lat.replace(" ", "")
        long_lat_list = object_long_lat.split(",")

        if len(long_lat_list) != 2:
            return None

        # convert to float values
        conv_long_lat_list = []
        for long_lat in long_lat_list:
            try:
                conv_long_lat_list.append(float(long_lat))
            except ValueError:
                return None



        geo_feature_dict = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": conv_long_lat_list
            },
            "properties": self.props
        }

        return geo_feature_dict
