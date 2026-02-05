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
    IIIF_IMAGE_SERVER_ORIGIN = "http://localhost:18080"

    POLLIN_TOML_VERSION = "0.0.0"
    POLLIN_TOML_TITLE = "Test Project"

    TEST_JS_FILE_CONTENT = "console.log('Hello, World!');"
    TEST_CSS_FILE_CONTENT = "body { font-family: Arial; }"
    TEST_LOGO_FILE_CONTENT = b"\x89PNG\r\n\x1a\n"

    DANGEROUS_GAMS3_PRODUCTION_ORIGIN = "https://gams.uni-graz.at"
    DANGEROUS_GAMS5_PRODUCTION_ORIGIN = "https://gams.uni-graz.at"

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
            UI_TITLE=TestPollinProject.POLLIN_TOML_TITLE,
            POLLIN_MODE="build",
            IIIF_IMAGE_SERVER_ORIGIN=TestPollinProject.IIIF_IMAGE_SERVER_ORIGIN,
            DANGEROUS_GAMS3_PRODUCTION_ORIGIN=TestPollinProject.DANGEROUS_GAMS3_PRODUCTION_ORIGIN,
            DANGEROUS_GAMS5_PRODUCTION_ORIGIN=TestPollinProject.DANGEROUS_GAMS5_PRODUCTION_ORIGIN
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
            PROJECT_ABBR = "{self.PROJECT_ABBR}"
            
            [dangerous]
            GAMS3_PRODUCTION_ORIGIN = "{TestPollinProject.DANGEROUS_GAMS3_PRODUCTION_ORIGIN}"
            GAMS5_PRODUCTION_ORIGIN = "{TestPollinProject.DANGEROUS_GAMS5_PRODUCTION_ORIGIN}"
            
            [dev]
            GAMS_API_ORIGIN = "{TestPollinProject.GAMS_API_ORIGIN}"
            IIIF_IMAGE_SERVER_ORIGIN = "{TestPollinProject.IIIF_IMAGE_SERVER_ORIGIN}"
            
            [stage]
            GAMS_API_ORIGIN = "{TestPollinProject.GAMS_API_ORIGIN}"
            IIIF_IMAGE_SERVER_ORIGIN = "{TestPollinProject.IIIF_IMAGE_SERVER_ORIGIN}"
            
            [build]
            GAMS_API_ORIGIN = "{TestPollinProject.GAMS_API_ORIGIN}"
            IIIF_IMAGE_SERVER_ORIGIN = "{TestPollinProject.IIIF_IMAGE_SERVER_ORIGIN}"
            
            [ui]
            VERSION = "{TestPollinProject.POLLIN_TOML_VERSION}"
            TITLE = "{TestPollinProject.POLLIN_TOML_TITLE}"
        """

        self._config.project_config_toml.write_text(config)

        templates_folder_path = Path(__file__).parent.parent / "resources" / "test" / "templates"

        # Load project.j2 template content from resources
        project_template_path = templates_folder_path / "project.j2"
        project_j2_content = project_template_path.read_text(encoding="utf-8")

        # Load object.j2 template content from resources
        object_template_path = templates_folder_path / "object.j2"
        object_j2_content = object_template_path.read_text(encoding="utf-8")

        # Load object-list.j2 template content from resources
        object_list_template_path = templates_folder_path / "object-list.j2"
        object_list_j2_content = object_list_template_path.read_text(encoding="utf-8")

        # Create basic templates as temp files
        (self._config.project_src_view_template_dir / "project.j2").write_text(project_j2_content)
        (self._config.project_src_view_template_dir / "object.j2").write_text(object_j2_content)
        (self._config.project_src_view_template_dir / "object-list.j2").write_text(object_list_j2_content)

        # Create basic static files
        self.get_test_css_path().parent.mkdir(parents=True, exist_ok=True)
        self.get_test_css_path().write_text(TestPollinProject.TEST_CSS_FILE_CONTENT)
        self.get_test_js_path().parent.mkdir(parents=True, exist_ok=True)
        self.get_test_js_path().write_text(TestPollinProject.TEST_JS_FILE_CONTENT)
        self.get_test_logo_path().parent.mkdir(parents=True, exist_ok=True)
        self.get_test_logo_path().write_bytes(TestPollinProject.TEST_LOGO_FILE_CONTENT)

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
