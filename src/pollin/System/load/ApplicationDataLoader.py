import logging

from pollin.System.load.DigitalObjectService import DigitalObjectService
from pollin.System.load.ProjectService import ProjectService
from pollin.System.init.ApplicationContext import ApplicationContext
from typing import List

class ApplicationDataLoader:
    """
    Encapsulates the loading data required for the application (on startup)
    """

    app_context: ApplicationContext
    """
    The application context
    """

    def __init__(self, app_context: ApplicationContext):
        # TODO validate correct setup of the app_context?
        self.app_context = app_context


    def limit_project_objects(self, object_ids: List[str]):
        """
        Returns a limited list of object ids based on the external configuration passed via the ApplicationContext
        :param object_ids: The original list of object ids
        :return: The limited list of object ids
        """
        limited_objects = []
        external_config = self.app_context.get_config().project_external_config
        if external_config:
            required_object_count = external_config.get_obj_count_restriction()
            required_object_ids = external_config.get_obj_required()
            # if no restrictions are defined, just use all available objects
            if not required_object_count and not required_object_ids:
                logging.debug("No object count restriction or required objects defined in the external configuration. Using all available objects.")
                return object_ids

            # restrict object count if defined
            if required_object_count:
                logging.info(f"Limiting the number of objects to {required_object_count} based on external configuration.")
                limited_objects = object_ids[:required_object_count]

            # ensure required objects are loaded
            if required_object_ids:
                logging.info(f"Ensuring that the following required objects are loaded: {required_object_ids} based on external configuration.")
                for id in required_object_ids:
                    limited_objects.append(id)

            # remove possible doubles in all_project_objects
            limited_objects = list(set(limited_objects))
            return limited_objects
        else:
            return object_ids


    def load(self):
        """
        Loads the data required for the application (digital objects, project data, but also customizable scripts etc.)
        :return:
        """

        # load project metadata from GAMS5
        project_data = ProjectService(self.app_context).load()
        self.app_context.get_app_data_store().set_project_data(project_data)

        # load object data
        digital_object_service = DigitalObjectService(self.app_context)
        object_ids = digital_object_service.load_project_object_ids(self.app_context.get_config().project)
        # optionally limit the number of objects according to external configuration
        object_ids = self.limit_project_objects(object_ids)
        # load detailed object data
        digital_objects = digital_object_service.load_project_objects(self.app_context.get_config().project, object_ids)
        self.app_context.get_app_data_store().set_objects(digital_objects)
