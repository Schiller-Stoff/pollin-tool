from pathlib import Path
from pollin.init.config.AppEnv import AppEnv
from pollin.init.config.ApplicationCacheConfig import ApplicationCacheConfig
from pollin.init.config.ApplicationConfiguration import ApplicationConfiguration
from utils.TestProject import TestProject


class TestPollinProject:
    """
    A utility class to create a temporary Pollin project structure for testing purposes.
    root_dir: Path - The root directory where the temporary project will be created.
    """

    project_dir: Path
    """
    The path to the temporary project directory
    """

    _config: ApplicationConfiguration

    PROJECT_ABBR = TestProject.PROJECT_ABBR

    GAMS_API_ORIGIN = "http://localhost:18085"

    POLLIN_TOML_VERSION = "0.0.0"
    POLLIN_TOML_TITLE = "Test Project"

    def __init__(self, root_dir: Path):
        self.project_dir = root_dir

        self._config = self._calc_config()
        self._create_file_structure()

    def get_project_dir(self) -> Path:
        """
        :return: The path to the temporary project directory
        """
        return self.project_dir


    def get_config(self) -> ApplicationConfiguration:
        """
        :return: The ApplicationConfiguration for the test project
        """
        if not self._config:
            raise ValueError("Configuration has not been initialized.")
        return self._config

    def _calc_config(self) -> ApplicationConfiguration:
        """
        :return: A basic ApplicationConfiguration for the test project
        """

        test_config = ApplicationConfiguration(
            project=TestPollinProject.PROJECT_ABBR,
            gams_host=TestPollinProject.GAMS_API_ORIGIN,
            project_files_root=self.project_dir,
            output_path=None,
            mode="build"
        )

        # storing same variables in ENV reference (used at runtime in templates)
        test_config.ENV = AppEnv(
            GAMS_API_ORIGIN=test_config.gams_host,
            PROJECT_ABBR=test_config.project,
            UI_VERSION=TestPollinProject.POLLIN_TOML_VERSION,
            UI_TITLE=TestPollinProject.POLLIN_TOML_TITLE
        )

        test_config.project_external_config = {
            "project": {
                "projectAbbr": TestPollinProject.PROJECT_ABBR
            },
            "dev": {
                "gamsApiOrigin": TestPollinProject.GAMS_API_ORIGIN
            },
            "build": {
                "gamsApiOrigin": TestPollinProject.GAMS_API_ORIGIN
            },
            "ui": {
                "version": TestPollinProject.POLLIN_TOML_VERSION,
                "title": TestPollinProject.POLLIN_TOML_TITLE
            }
        }


        test_config.cache = ApplicationCacheConfig(
            cache_dir=Path(self.project_dir) / ".pollin_cache",
            enabled=False
        )

        return test_config


    def _create_file_structure(self):
        """
        Creates a basic Pollin project file structure in the temporary directory.
        """
        if not self._config:
            raise ValueError("Configuration must be set before creating file structure.")



        # Create directories
        self._config.project_src_view_template_dir.mkdir(parents=True)
        self._config.project_src_static_dir.mkdir(parents=True)

        # Create config file
        config = f"""
            [project]
            projectAbbr = "{self.PROJECT_ABBR}"
            
            [dev]
            gamsApiOrigin = "{TestPollinProject.GAMS_API_ORIGIN}"
            
            [build]
            gamsApiOrigin = "{TestPollinProject.GAMS_API_ORIGIN}"
            
            [ui]
            version = "{TestPollinProject.POLLIN_TOML_VERSION}"
            title = "{TestPollinProject.POLLIN_TOML_TITLE}"
        """

        self._config.project_config_toml.write_text(config)

        # TODO hardcoded test values also needed outside?

        # Create basic templates
        (self._config.project_src_view_template_dir / "project.j2").write_text(
            "<h1>{{ project.projectAbbr }}</h1>"
        )
        (self._config.project_src_view_template_dir / "object.j2").write_text(
            "<h1>{{ object.db.baseMetadata.title }}</h1>"
        )
        (self._config.project_src_view_template_dir / "object-list.j2").write_text(
            "<h1>{{ objects[0].title }}</h1>"
        )

        # Create basic static files
        self.get_test_css_path().parent.mkdir(parents=True, exist_ok=True)
        self.get_test_css_path().write_text("body { font-family: Arial; }")
        self.get_test_js_path().parent.mkdir(parents=True, exist_ok=True)
        self.get_test_js_path().write_text("console.log('Hello, World!');")
        self.get_test_logo_path().parent.mkdir(parents=True, exist_ok=True)
        self.get_test_logo_path().write_bytes(b"\x89PNG\r\n\x1a\n")



    def get_test_css_path(self):
        """
        :return: The path to the test CSS file
        """
        return self._config.project_src_static_dir / "css" / "styles.css"

    def get_test_js_path(self):
        """
        :return: The path to the test JS file
        """
        return self._config.project_src_static_dir / "js" / "scripts.js"

    def get_test_logo_path(self):
        """
        :return: The path to the test logo file
        """
        return self._config.project_src_static_dir / "images" / "logo.png"
