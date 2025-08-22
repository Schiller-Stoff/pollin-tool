import logging
import pathlib
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

    def configure(self, directory: str, mode: Literal["dev", "build"] = "dev"):
        """
        Sets configuration params on the ApplicationContext
        :return:
        """
        if mode not in ["dev", "build"]:
            raise ValueError("Mode must be either 'dev' or 'build'")

        # load possible external configuration
        external_config = ApplicationExternalConfigImporter.import_config(
            pathlib.Path(directory) / ApplicationConfiguration.CONFIG_FILE_NAME,
            mode
        )
        external_config_parsed = ApplicationExternalConfig(external_config, mode)
        logging.info(f"External configuration loaded {external_config}")

        app_config = ApplicationConfiguration(
            project=external_config_parsed.get_project_abbr(),
            gams_host=external_config_parsed.get_gams_api_origin(),
            project_files_root=Path(directory),
            output_path=external_config_parsed.get_output_path(), # returns None if not set in config
            mode=mode
        )

        # storing same variables in ENV reference (used at runtime in templates)
        app_config.ENV = AppEnv(
            GAMS_API_ORIGIN=app_config.gams_host,
            PROJECT_ABBR=app_config.project,
            UI_VERSION=external_config_parsed.get_ui_version(),
            UI_TITLE=external_config_parsed.get_ui_title()
        )
        self.app_context.set_config(app_config)
        self.app_context.get_config().project_external_config = external_config_parsed



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

