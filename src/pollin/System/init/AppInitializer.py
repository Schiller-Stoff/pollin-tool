import logging
from pathlib import Path

from pollin.System.init.AppEnv import AppEnv
from pollin.System.init.ApplicationContext import ApplicationContext
from pollin.System.init.ApplicationConfiguration import ApplicationConfiguration
from pollin.System.init.ApplicationExternalConfig import ApplicationExternalConfig
from pollin.System.init.ApplicationExternalConfigImporter import ApplicationExternalConfigImporter
from pollin.System.load.utils.Pyrilo import Pyrilo
from importlib import resources as impresources
from pollin.System.load.ApplicationDatastore import ApplicationDatastore

class AppInitializer:

    app_context: ApplicationContext

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context


    def configure(self, project:str, host: str, directory: str):
        """
        Sets configuration params on the ApplicationContext
        :return:
        """
        app_config = ApplicationConfiguration()

        app_config.gams_host = host
        app_config.project = project

        # storing same variables in ENV reference (used at runtime in templates)
        app_config.ENV = AppEnv(GAMS_API_ORIGIN=app_config.gams_host, PROJECT_ABBR=app_config.project)

        # set folder locations
        app_config.project_files_root = Path(directory)
        # set project configuration file
        app_config.project_config_json = app_config.project_files_root / "pollin.json"
        # src folder (~files that need to be watched)
        app_config.project_src_dir = app_config.project_files_root / "src"
        # set view template directory
        app_config.project_src_view_template_dir = app_config.project_src_dir / "templates"
        # pages view directory
        app_config.project_src_view_template_pages_dir = app_config.project_src_view_template_dir / "pages"
        # static directory src folder
        app_config.project_src_static_dir = app_config.project_src_dir / "static"

        # scripts directory
        app_config.project_scripts_dir = app_config.project_files_root / "scripts"

        # internal setup folder
        app_config.intern_setup_dir = impresources.files('pollin') / "setup"
        # internal src folder
        app_config.intern_src_dir = impresources.files('pollin') / "setup" / "src"
        # set internal template directory
        app_config.intern_template_dir = impresources.files('pollin') / "setup" / "src" /  "templates"


        # reference to public folder
        app_config.public_dir = app_config.project_files_root / "public"
        app_config.project_public_dir = app_config.public_dir.joinpath(project)
        # static directory public folder
        app_config.project_public_static_dir = app_config.project_public_dir / "static"

        self.app_context.set_config(app_config)
        return self

    def init_context_beans(self):
        """

        :return:
        """
        logging.basicConfig( encoding='utf-8', level=logging.INFO)
        logging.info("*** Starting poll-in cli")

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

        # load possible external configuration
        external_config = ApplicationExternalConfigImporter(self.app_context).import_config()
        if external_config:
            external_config_parsed = ApplicationExternalConfig(external_config)
            self.app_context.get_config().project_external_config = external_config_parsed
            logging.info(f"External configuration loaded {external_config}")

        return self
