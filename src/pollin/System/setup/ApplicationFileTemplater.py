import logging
import os
import shutil
from pathlib import Path
from pollin.System.init.ApplicationContext import ApplicationContext

class ApplicationFileTemplater:
    """
    Generates template files for the application
    """

    app_context: ApplicationContext
    """
    The application context
    """

    def __init__(self, app_context: ApplicationContext):
        """
        :param app_context:
        """
        self.app_context = app_context


    def setup(self):
        """
        Initializes the project structure for GAMS5
        :return:
        """
        project_files_root = self.app_context.get_config().project_files_root
        intern_setup_dir = self.app_context.get_config().intern_setup_dir
        project_public_dir = self.app_context.get_config().project_public_dir
        public_dir = self.app_context.get_config().public_dir

        # check if project_files_root exists and ist not empty
        if not os.path.exists(project_files_root):
            msg = f"*** Project root folder at {project_files_root} does not exist***"
            logging.error(msg)
            raise FileNotFoundError(msg)

        if len(os.listdir(project_files_root)) > 0:
            msg = f"*** Project root folder at {project_files_root} is not empty***"
            logging.error(msg)
            raise FileExistsError(msg)

        # copy over the internal setup files
        shutil.copytree(intern_setup_dir, project_files_root, dirs_exist_ok=True)

        # setup public folder (with project folder)
        if not os.path.exists(project_public_dir):
            os.makedirs(project_public_dir)
            Path(public_dir).mkdir(parents=True, exist_ok=True)

        logging.info(f"*** Successfully set up project template files at *** {public_dir}")