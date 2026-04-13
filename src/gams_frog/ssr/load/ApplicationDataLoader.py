import logging

from gams_frog.ssr.load.DigitalObjectService import DigitalObjectService
from gams_frog.ssr.load.ProjectService import ProjectService
from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from typing import List
from gams_frog.ssr.load.cache.DataCacheManager import DataCacheManager


class ApplicationDataLoader:
    """
    Encapsulates the loading data required for the application (on startup)
    """

    app_context: ApplicationContext
    """
    The application context
    """

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context
        self.cache_manager = DataCacheManager(app_context)


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
        project_abbr = self.app_context.get_config().project

        # Try to load from cache first
        cached_project_data = self.cache_manager.get_cached_project_data(project_abbr)
        cached_objects = self.cache_manager.get_cached_objects(project_abbr)

        if cached_project_data and cached_objects:
            logging.info(f"Using cached data for project {project_abbr}")
            self.app_context.get_app_data_store().set_project_data(cached_project_data)
            self.app_context.get_app_data_store().set_objects(cached_objects)
            return

        # Cache miss or invalid - load from API
        logging.info(f"Loading fresh data from API for project {project_abbr}")

        # Load project metadata from GAMS5
        if not cached_project_data:
            project_data = ProjectService(self.app_context).load()
            self.app_context.get_app_data_store().set_project_data(project_data)
            self.cache_manager.cache_project_data(project_abbr, project_data)
        else:
            self.app_context.get_app_data_store().set_project_data(cached_project_data)

        # Load object data
        if not cached_objects:
            digital_object_service = DigitalObjectService(self.app_context)
            object_ids = digital_object_service.load_project_object_ids(project_abbr)

            # Optionally limit the number of objects according to external configuration
            object_ids = self.limit_project_objects(object_ids)

            # Load detailed object data
            digital_objects = digital_object_service.load_project_objects(project_abbr, object_ids)
            self.app_context.get_app_data_store().set_objects(digital_objects)

            # Cache the loaded objects
            self.cache_manager.cache_objects(project_abbr, digital_objects)
        else:
            self.app_context.get_app_data_store().set_objects(cached_objects)

