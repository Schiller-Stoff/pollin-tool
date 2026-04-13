import pathlib
from os import PathLike
from typing import Literal

from gams_frog.ssr.init.config.AppEnv import AppEnv
from gams_frog.ssr.init.config.ApplicationExternalConfig import ApplicationExternalConfig
from gams_frog.ssr.init.config.ApplicationCacheConfig import ApplicationCacheConfig


class ApplicationConfiguration:
    """
    Configuration class for the main program.

    """

    project: str
    """
    Abbreviation of the project
    """

    gams_host: str
    """
    The host of the GAMS5 instance
    """

    project_files_root: PathLike
    """
    The root folder of the project files (views / public etc.)
    """

    _output_path: PathLike | None = None
    """
    The output path where the build files should be placed.
    """

    mode:  Literal["dev", "build", "stage"] = "dev"
    """
    The mode the gams_frog tool is running in, either 'develop' or 'production'.
    """

    ENV: AppEnv
    """
    Stores runtime env variables needed in the templates, e.g. set gams-api host
    """

    CONFIG_FILE_NAME: str = "gams_frog.toml"

    cache: ApplicationCacheConfig
    """
    Configuration for caching
    """

    PROJECT_DEPLOYMENT_FOLDER: str = "pub"
    """
    Root path of the gams_frog project on the deployment webserver
    """

    def alternative_output_path_set(self) -> bool:
        """
        Checks if an alternative output path is set
        :return: bool
        """
        return self._output_path is not None

    @property
    def public_dir(self) -> pathlib.Path:
        """
        Points to the public folder e.g. "public"
        :return: PathLike
        """
        if self._output_path:
            return pathlib.Path(self._output_path)
        # if no output path is set, use the default public directory
        # which is the project files root
        return pathlib.Path(self.project_files_root) / "public"

    @property
    def project_src_dir(self) -> pathlib.Path:
        """
        'src'-folder
        The source directory of the project files needed for building the project frontends
        (files that need to be watched for changes)
        :return: PathLike
        """
        return pathlib.Path(self.project_files_root) / "src"

    @property
    def project_src_static_dir(self) -> pathlib.Path:
        """
        The directory where the static files are stored in the project files src structure
        :return: PathLike
        """
        return pathlib.Path(self.project_src_dir) / "static"

    @property
    def project_src_view_template_dir(self) -> pathlib.Path:
        """
        The directory where the view templates are stored in the project files src structure
        :return: PathLike
        """
        return pathlib.Path(self.project_src_dir) / "templates"

    @property
    def project_src_view_template_pages_dir(self) -> pathlib.Path:
        """
        Points to the pages directory of the project view templates
        :return: PathLike
        """
        return pathlib.Path(self.project_src_view_template_dir) / "pages"

    @property
    def project_public_dir(self) -> pathlib.Path:
        """
        Points to the public directory of the project e.g. public/memo
        :return: PathLike
        """
        return pathlib.Path(self.public_dir) / "pub" / self.project

    @property
    def project_public_static_dir(self) -> pathlib.Path:
        """
        Points to the public static directory of the project
        :return: PathLike
        """
        return pathlib.Path(self.project_public_dir) / "static"

    @property
    def project_config_toml(self) -> pathlib.Path:
        """
        Points to the path of the project configuration file
        :return: PathLike
        """
        return pathlib.Path(self.project_files_root) / self.CONFIG_FILE_NAME

    project_external_config: ApplicationExternalConfig | None = None
    """
    Contains the external configuration of the project or None if not available
    """


    def __init__(self, project: str, gams_host: str, project_files_root: PathLike, output_path: PathLike | None = None, mode: Literal["dev", "build", "stage"] = "dev"):
        self.project = project
        self.gams_host = gams_host
        self.project_files_root = project_files_root
        self._output_path = output_path
        self.mode = mode

