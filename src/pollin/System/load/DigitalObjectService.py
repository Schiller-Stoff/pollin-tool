from pollin.System.common.DigitalObjectViewModel import DigitalObjectViewModel
from pollin.System.init.ApplicationContext import ApplicationContext
from typing import List


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
            digital_object = DigitalObjectViewModel(dc_json, object_metadata, {}, {})
            digital_objects.append(digital_object)

        return digital_objects
