import logging
import shutil
from pathlib import Path
from typing import Literal
from pollin.System.init.AppEnv import AppEnv
from pollin.System.init.ApplicationContext import ApplicationContext
from pollin.System.init.ApplicationConfiguration import ApplicationConfiguration
from pollin.System.init.ApplicationExternalConfig import ApplicationExternalConfig
from pollin.System.init.ApplicationExternalConfigImporter import ApplicationExternalConfigImporter
from pollin.System.load.utils.Pyrilo import Pyrilo
from pollin.System.load.ApplicationDatastore import ApplicationDatastore

class AppInitializer:

    app_context: ApplicationContext

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context

    def configure(self, project:str, host: str, directory: str, output_path: str = None, mode: Literal["develop", "production"] = "develop"):
        """
        Sets configuration params on the ApplicationContext
        :return:
        """
        if mode not in ["develop", "production"]:
            raise ValueError("Mode must be either 'develop' or 'production'")

        app_config = ApplicationConfiguration(
            project=project,
            gams_host=host,
            project_files_root=Path(directory),
            output_path=Path(output_path) if output_path else None,
            mode=mode
        )

        # storing same variables in ENV reference (used at runtime in templates)
        app_config.ENV = AppEnv(GAMS_API_ORIGIN=app_config.gams_host, PROJECT_ABBR=app_config.project)
        self.app_context.set_config(app_config)

        # load possible external configuration
        external_config = ApplicationExternalConfigImporter(self.app_context).import_config()
        if external_config:
            external_config_parsed = ApplicationExternalConfig(external_config)
            self.app_context.get_config().project_external_config = external_config_parsed
            logging.info(f"External configuration loaded {external_config}")

        return self

    def init_context_beans(self):
        """

        :return:
        """
        logging.basicConfig( encoding='utf-8', level=logging.INFO)
        logging.info("*** Starting poll-in cli in mode: %s ***", self.app_context.get_config().mode)

        # init datastore
        self.app_context.set_app_data_store(ApplicationDatastore())

        # init pyrilo with default values
        self.app_context.set_pyrilo(
            Pyrilo("http://localhost:18085", "api/v1")
        )
        if self.app_context.get_config().gams_host:
            self.app_context.get_pyrilo().configure(
                self.app_context.get_config().gams_host,
            "api/v1")

        return self

    def setup(self):
        """
        Sets up files, folder needed for the application to run.
        Ensures that locations specified in the config actually exist and are in a clean state.
        """

        # if not public folder exist -> create
        if not self.app_context.get_config().project_public_dir.exists():
            self.app_context.get_config().project_public_dir.mkdir(parents=True)
        # else delete complete tree and recreate
        else:
            shutil.rmtree(self.app_context.get_config().project_public_dir)
            self.app_context.get_config().project_public_dir.mkdir(parents=True)

