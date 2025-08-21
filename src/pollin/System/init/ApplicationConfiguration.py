import pathlib
from os import PathLike
from typing import Literal

from pollin.System.init.AppEnv import AppEnv
from pollin.System.init.ApplicationExternalConfig import ApplicationExternalConfig

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

    mode: Literal["develop", "production"] = "develop"
    """
    The mode the pollin tool is running in, either 'develop' or 'production'.
    """

    ENV: AppEnv
    """
    Stores runtime env variables needed in the templates, e.g. set gams-api host
    """

    def alternative_output_path_set(self) -> bool:
        """
        Checks if an alternative output path is set
        :return: bool
        """
        return self._output_path is not None

    @property
    def public_dir(self) -> PathLike:
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
    def project_src_dir(self) -> PathLike:
        """
        'src'-folder
        The source directory of the project files needed for building the project frontends
        (files that need to be watched for changes)
        :return: PathLike
        """
        return pathlib.Path(self.project_files_root) / "src"

    @property
    def project_src_static_dir(self) -> PathLike:
        """
        The directory where the static files are stored in the project files src structure
        :return: PathLike
        """
        return pathlib.Path(self.project_src_dir) / "static"

    @property
    def project_src_view_template_dir(self) -> PathLike:
        """
        The directory where the view templates are stored in the project files src structure
        :return: PathLike
        """
        return pathlib.Path(self.project_src_dir) / "templates"

    @property
    def project_src_view_template_pages_dir(self) -> PathLike:
        """
        Points to the pages directory of the project view templates
        :return: PathLike
        """
        return pathlib.Path(self.project_src_view_template_dir) / "pages"

    @property
    def project_public_dir(self) -> PathLike:
        """
        Points to the public directory of the project e.g. public/memo
        :return: PathLike
        """
        return pathlib.Path(self.public_dir) / self.project

    @property
    def project_public_static_dir(self) -> PathLike:
        """
        Points to the public static directory of the project
        :return: PathLike
        """
        return pathlib.Path(self.project_public_dir) / "static"

    @property
    def project_config_toml(self) -> PathLike:
        """
        Points to the path of the project configuration file
        :return: PathLike
        """
        return pathlib.Path(self.project_files_root) / "pollin.toml"

    project_external_config: ApplicationExternalConfig | None = None
    """
    Contains the external configuration of the project or None if not available
    """


    def __init__(self, project: str, gams_host: str, project_files_root: PathLike, output_path: PathLike | None = None, mode: Literal["develop", "production"] = "develop"):
        self.project = project
        self.gams_host = gams_host
        self.project_files_root = project_files_root
        self._output_path = output_path
        self.mode = mode

