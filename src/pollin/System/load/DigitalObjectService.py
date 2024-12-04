import json
import logging
from pathlib import Path
from pollin.System.load.utils.XMLWebComponentConverter import XMLWebComponentConverter
from pollin.System.common.DigitalObjectViewModel import DigitalObjectViewModel
from pollin.System.init.ApplicationContext import ApplicationContext
from typing import List, Dict


class DigitalObjectService:
    """
    Service class for loading digital objects from the GAMS
    """

    app_context: ApplicationContext
    """
    The application context
    """

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context


    def load_project_object_ids(self, project: str):
        """
        Loads digital object ids from the GAMS5 instance
        :param project: The project abbreviation
        """
        pyrilo = self.app_context.get_pyrilo()
        all_project_object_id_dicts = pyrilo.list_objects(project)
        all_project_object_ids = [project_object["id"] for project_object in all_project_object_id_dicts]
        return all_project_object_ids


    def load_project_objects(self,project: str, project_object_ids: List[str]):
        """
        Loads digital objects from the GAMS5 instance
        :param project_objects:
        :return:
        """
        pyrilo = self.app_context.get_pyrilo()

        digital_objects = []

        for project_object_id in project_object_ids:
            object_id = project_object_id
            object_metadata = pyrilo.get_object(project, object_id)
            dc_json = pyrilo.get_dublin_core(project, object_id)

            object_datastream_ids = object_metadata.get("datastreams", [])
            component_map = self._load_component_map(object_id, object_datastream_ids)

            try:
                search_json = pyrilo.get_search_json(project, object_id)
                digital_object = DigitalObjectViewModel(dc_json, object_metadata, search_json, component_map)
            except ConnectionError as e:
                # if the search.json is not available, we can still load the object
                logging.warning(f"Could not load search.json for object {object_id}. Error: {e}")
                digital_object = DigitalObjectViewModel(dc_json, object_metadata, {}, component_map)

            digital_objects.append(digital_object)

        return digital_objects


    def _load_component_map(self, object_id: str, datastreams: List[str]) -> Dict[str, str]:
        """
        Loads additional .xml datastreams data and converts them to web components in the form of a dictionary
        (per dsid and mapped html)
        :param object_id: The object id
        :param datastreams: The list of datastream-ids
        :return: The dictionary containing the web components. Returns empty dictionary if no datastreams are available.
        """
        # loads additional datastream data
        object_datastreams: List[str] = datastreams
        datastream_web_components = {}
        for ds_id in object_datastreams:
            if ds_id.endswith(".xml"):
                project_abbr = self.app_context.get_config().project
                source_bytes = self.app_context.get_pyrilo().get_datastream_content(project_abbr, object_id, ds_id)
                template_accessor = ds_id.replace(".xml", "").lower()
                datastream_web_components[template_accessor] = XMLWebComponentConverter.xml_to_webcomponent(source_bytes.decode("utf-8"), f"{project_abbr}-")

        return datastream_web_components

    # TODO refactor
    @staticmethod
    def aggregate_index_json(output_dir: str, data: list[DigitalObjectViewModel]):
        """
        Aggregates a singular json containing data about all digital objects (used for client side searches etc.)
        :param data: list of DigitalObjects
        :return:
        """

        index_json = []
        for digital_object in data:
            index_json.append(digital_object.to_dict())

        json_str = json.dumps(index_json, ensure_ascii=False, indent=4)
        json_file_path = Path(output_dir).joinpath("object_index.json")

        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(json_str)
            logging.info(f"Successfully wrote {json_file_path} to file")

    # TODO refactor
    @staticmethod
    def aggregate_geo_json(output_dir: str, data: list[DigitalObjectViewModel]):
        """
        Creates a geo json file containing all objects with geo data (in the search.json)
        :param output_dir: The output directory
        :param data: list of DigitalObjects
        :return:
        """

        geo_json_dict = {
            "type": "FeatureCollection",
            "features": []
        }

        index_json = geo_json_dict["features"]
        for digital_object in data:
            geo_feature = digital_object.to_geo_point_feature()
            if geo_feature:
                index_json.append(geo_feature)

        json_str = json.dumps(geo_json_dict, ensure_ascii=False, indent=4)
        json_file_path = Path(output_dir).joinpath("object_index_geo.json")

        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(json_str)
            logging.info(f"Successfully wrote {json_file_path} to file")