import logging
import pathlib
import shutil
from pathlib import Path
from typing import Literal
from gams_frog.ssr.init.config.AppEnv import AppEnv
from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from gams_frog.ssr.init.config.ApplicationConfiguration import ApplicationConfiguration
from gams_frog.ssr.init.config.ApplicationExternalConfig import ApplicationExternalConfig
from gams_frog.ssr.init.config.ApplicationExternalConfigImporter import ApplicationExternalConfigImporter
from gams_frog.ssr.init.config.ApplicationCacheConfig import ApplicationCacheConfig
from gams_frog.ssr.load.utils.Pyrilo import Pyrilo
from gams_frog.ssr.load.ApplicationDatastore import ApplicationDatastore


class AppInitializer:
    app_context: ApplicationContext

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context

    def configure(
            self,
            directory: str,
            mode: Literal["dev", "build", "stage"] = "dev",
            dev_server_port: int | None = None,
    ):
        """
        Sets configuration params on the ApplicationContext.

        :param directory: Path to the project root containing .toml.
        :param mode: Active gams-frog mode.
        :param dev_server_port: Only meaningful in dev mode. When provided, the configured
            [dev].GAMS_API_ORIGIN is promoted to `proxy_target_origin` (where the dev server
            forwards /api/* to), and env.GAMS_API_ORIGIN — what templates see — is rewritten
            to the local dev-server origin so browser calls stay same-origin and avoid CORS.
            When None in dev mode, the proxy is not activated and templates see the raw
            configured upstream (legacy behavior).
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
            output_path=external_config_parsed.get_output_path(),  # returns None if not set in config
            mode=mode
        )

        # Dev proxy wiring: the configured GAMS_API_ORIGIN becomes the upstream the proxy
        # forwards to; templates see the local dev server origin so the browser treats API
        # calls as same-origin. See ApiProxyHandler.
        # gams_host stays the real upstream — it's used server-side by Pyrilo and for
        # stable cache keys across dev-server port changes.
        if mode == "dev" and dev_server_port is not None:
            app_config.proxy_target_origin = app_config.gams_host
            template_visible_gams_origin = f"http://localhost:{dev_server_port}"
            logging.info(
                f"*** Dev proxy target: {app_config.proxy_target_origin} "
                f"(templates will see env.GAMS_API_ORIGIN = {template_visible_gams_origin})"
            )
        else:
            template_visible_gams_origin = app_config.gams_host

        # storing same variables in ENV reference (used at runtime in templates)
        app_config.ENV = AppEnv(
            GAMS_API_ORIGIN=template_visible_gams_origin,
            PROJECT_ABBR=app_config.project,
            UI_VERSION=external_config_parsed.get_ui_version(),
            UI_TITLE=external_config_parsed.get_ui_title(),
            GAMS_FROG_MODE=mode,
            IIIF_IMAGE_SERVER_ORIGIN=external_config_parsed.get_iiif_image_server_origin(),
            DANGEROUS_GAMS3_PRODUCTION_ORIGIN=external_config_parsed.get_gams3_production_origin(),
            DANGEROUS_GAMS5_PRODUCTION_ORIGIN=external_config_parsed.get_gams5_production_origin()
        )
        self.app_context.set_config(app_config)
        self.app_context.get_config().project_external_config = external_config_parsed

        # set cache config
        cache_enabled = mode == "dev"
        self.app_context.get_config().cache = ApplicationCacheConfig(
            cache_dir=Path(directory) / ".gams_frog_cache",
            enabled=cache_enabled
        )

        return self

    def init_context_beans(self):
        """

        :return:
        """
        logging.basicConfig(encoding='utf-8', level=logging.INFO)
        logging.info("*** Starting poll-in cli in mode: %s ***", self.app_context.get_config().mode)

        # init datastore
        self.app_context.set_app_data_store(ApplicationDatastore())

        # init pyrilo with default values
        self.app_context.set_pyrilo(
            Pyrilo("http://localhost:18085", "api/curation/v1")
        )
        if self.app_context.get_config().gams_host:
            self.app_context.get_pyrilo().configure(
                self.app_context.get_config().gams_host,
                "api/curation/v1")

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

