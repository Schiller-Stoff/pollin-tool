import logging
import pathlib
import shutil
from pathlib import Path
from typing import Literal
from pollin.ssr.init.config.AppEnv import AppEnv
from pollin.ssr.init.ApplicationContext import ApplicationContext
from pollin.ssr.init.config.ApplicationConfiguration import ApplicationConfiguration
from pollin.ssr.init.config.ApplicationExternalConfig import ApplicationExternalConfig
from pollin.ssr.init.config.ApplicationExternalConfigImporter import ApplicationExternalConfigImporter
from pollin.ssr.init.config.ApplicationCacheConfig import ApplicationCacheConfig
from pollin.ssr.load.utils.Pyrilo import Pyrilo
from pollin.ssr.load.ApplicationDatastore import ApplicationDatastore

class AppInitializer:

    app_context: ApplicationContext

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context

    def configure(self, directory: str, mode: Literal["dev", "build", "stage"] = "dev"):
        """
        Sets configuration params on the ApplicationContext
        :return:
        """
        if mode not in ["dev", "build", "stage"]:
            raise ValueError("Mode must be either 'dev', 'stage' or 'build'")

        directory = str(Path(directory).resolve())  # resolve "." to absolute path

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
            UI_TITLE=external_config_parsed.get_ui_title(),
            POLLIN_MODE=mode,
            IIIF_IMAGE_SERVER_ORIGIN=external_config_parsed.get_iiif_image_server_origin(),
            DANGEROUS_GAMS3_PRODUCTION_ORIGIN=external_config_parsed.get_gams3_production_origin(),
            DANGEROUS_GAMS5_PRODUCTION_ORIGIN=external_config_parsed.get_gams5_production_origin()
        )
        self.app_context.set_config(app_config)
        self.app_context.get_config().project_external_config = external_config_parsed

        # set cache config
        cache_enabled = mode == "dev"
        self.app_context.get_config().cache = ApplicationCacheConfig(
            cache_dir=Path(directory) / ".pollin_cache",
            enabled=cache_enabled
        )

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

