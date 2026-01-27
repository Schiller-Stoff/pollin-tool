import json
import urllib
from typing import List, Any
import logging
from urllib.error import HTTPError
from xml.etree import ElementTree as ET

class Pyrilo:
    """
    Handles basic requests against GAMS5 REST-API.
    """

    HOST: str
    # do some error control? (should not contain trailing slashes etc.)
    API_BASE_PATH: str

    def __init__(self, host: str, api_base_path: str) -> None:
        self.HOST = host
        self.API_BASE_PATH = api_base_path


    def configure(self, host: str, api_base_path: str):
        """
        Configures the Pyrilo instance, like setting the host of GAMS5.
        """
        self.HOST = host
        self.API_BASE_PATH = api_base_path

    def list_objects(self, project_abbr: str) -> List[dict[str, Any]]:
        """
        Retrieves an overview over all digital objects for given project.

        """

        collected_objects = self._collect_objects(project_abbr, 0, [])
        # sorting objects by title
        collected_objects.sort(key=lambda x: x["baseMetadata"]["title"])
        return collected_objects


    def _collect_objects(self, project_abbr: str, startIndex: int, objectCollector: List[Any]) -> List[dict[str, Any]]:
        """
        Retrieves all digital objects for given project.

        """
        # TODO implement sorting in REST-API for json responses
        url = f"{self.HOST}/{self.API_BASE_PATH}/projects/{project_abbr}/objects?pageIndex={startIndex}&pageSize=1000&sortBy=baseMetadata.title"
        cur_request = urllib.request.Request(url)
        with urllib.request.urlopen(cur_request) as response:
            data = response.read()
            logging.debug(data)
            json_data =  json.loads(data.decode('utf-8'))

            pagination_result: List[Any] = json_data["results"]
            pagination_result_count = len(pagination_result)

            if pagination_result_count > 0:
                objectCollector.extend(pagination_result)
                logging.debug(f"Requesting digital objects for project {project_abbr} from {url} with pageIndex {startIndex}. Got objects: {len(json_data)}")
                return self._collect_objects(project_abbr, startIndex + 1, objectCollector)
            else:
                return objectCollector

    def get_object(self, project_abbr: str, object_id: str) -> dict[str, any]:
        """
        Retrieves a digital object for given project and object id.

        """

        url = f"{self.HOST}/{self.API_BASE_PATH}/projects/{project_abbr}/objects/{object_id}"
        logging.info(f"Requesting digital object with id {object_id} for project {project_abbr} from {url}")

        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                logging.debug(data)
                return json.loads(data.decode('utf-8'))
        except HTTPError as e:
            raise ConnectionError(f"Error while requesting digital object with id {object_id} for project {project_abbr} from url {url}. Error: {e}")


    def get_datastreams(self, project_abbr: str, object_id: str) -> dict[str, str]:
        """
        Requests a list of all datastreams for given digital object
        """
        url = f"{self.HOST}/{self.API_BASE_PATH}/projects/{project_abbr}/objects/{object_id}/datastreams?pageSize=1000"
        logging.info(f"Requesting datastreams for object with id {object_id} for project {project_abbr} from {url}")
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                logging.debug(data)
                parsed = json.loads(data.decode('utf-8'))
                return parsed["results"]
        except HTTPError as e:
            raise ConnectionError(f"Error while requesting datastreams from digital object with id {object_id} for project {project_abbr} from url {url}. Error: {e}")

    def get_datastream_content(self, project_abbr: str, object_id: str, ds_id: str) -> bytes:
        """
        Retrieves a datastream for given project, object id and datastream id.

        """

        url = f"{self.HOST}/{self.API_BASE_PATH}/projects/{project_abbr}/objects/{object_id}/datastreams/{ds_id}/content"
        logging.debug(f"Requesting datastream with id {ds_id} for object with id {object_id} for project {project_abbr} from {url}")

        try:
            with urllib.request.urlopen(url) as response:
                data: bytes = response.read()
                logging.debug(data)
                return data
        except HTTPError as e:
            msg = f"Error while requesting datastream with id {ds_id} for object with id {object_id} for project {project_abbr} from {url}. Error: {e}"
            logging.error(msg)
            raise ConnectionError(msg)


    def get_search_json(self, project_abbr: str, object_id: str):
        """
        Retrieves the search.json for a given object.
        """
        data = self.get_datastream_content(project_abbr, object_id, "SEARCH.json")
        return json.loads(data.decode('utf-8'))

    def get_dublin_core(self, project_abbr: str, object_id: str):
        """
        Retrieves the dublin core metadata for a given object.
        """
        dc_xml = self.get_datastream_content(project_abbr, object_id, "DC.xml")

        # Parse the XML file

        root = ET.fromstring(dc_xml)
        dc_dict = {}
        for child in root:
            # removes namespace from tag
            tag_name = child.tag.split("}")[1]

            # check if tagname already exists in dict
            if tag_name in dc_dict.keys():
                # if tagname already exists, we append the new value to the existing value
                dc_dict[tag_name].append(child.text)
            else:
                # if tagname does not exist, we create a new entry
                dc_dict[tag_name] = [child.text]


        logging.debug(f"fReturning now dc dict: {dc_dict}")
        return dc_dict


    def get_project(self, project_abbr) -> dict[str, any]:
        """
        Retrieves a project's metadata from GAMS5-api (like description)
        """

        url = f"{self.HOST}/{self.API_BASE_PATH}/projects/{project_abbr}"
        logging.info(f"Requesting {project_abbr} project's metadata from {url}")

        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                logging.debug(data)
                return json.loads(data.decode('utf-8'))
        except HTTPError as e:
            raise ConnectionError(f"Error while requesting project metadata from project {project_abbr} from url {url}. Error: {e}")


    def project_modified_since(self, project_abbr: str, last_modified: str) -> bool:
        """
        Checks if a project has been modified since the given timestamp.

        :param project_abbr: The project abbreviation
        :param last_modified: The last modified timestamp in ISO 8601 format
        :return: True if the project has been modified since the given timestamp, False otherwise
        """

        url = f"{self.HOST}/{self.API_BASE_PATH}/projects/{project_abbr}/objects"
        logging.debug(f"Checking if project {project_abbr} has been modified since {last_modified} from {url}")

        try:
            # send HEAD request with If-Modified-Since header
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('If-Modified-Since', last_modified)
            with urllib.request.urlopen(req) as response:
                # if we get a 200 response, the project has been modified
                if response.status == 200:
                    return True
                else:
                    msg = f"Received unexpected response status {response.status} while checking if project {project_abbr} has been modified since {last_modified} from url {url}."
                    logging.error(msg)
                    raise ConnectionError(msg)
        except HTTPError as e:
            if e.status == 304:
                # 304 means not modified
                return False

            msg = f"Error while checking if project {project_abbr} has been modified since {last_modified} from url {url}. Error: {e}"
            logging.error(msg)
            raise ConnectionError(msg)