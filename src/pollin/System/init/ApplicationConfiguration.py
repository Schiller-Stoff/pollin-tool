from os import PathLike

from pollin.System.init.AppEnv import AppEnv
from pollin.System.init.ApplicationExternalConfig import ApplicationExternalConfig

class ApplicationConfiguration:
    """
    Configuration class for the main program.
    TODO rename to ApplicationConfiguration?
    TODO general refactoring. Fields can be none
    """

    project: str| None
    """
    Abbreviation of the project
    """

    gams_host: str | None
    """
    The host of the GAMS5 instance
    """

    ENV: AppEnv
    """
    Stores runtime env variables needed in the templates, e.g. set gams-api host
    """

    project_files_root: PathLike
    """
    The root folder of the project files (views / public etc.)
    """

    project_src_dir: PathLike
    """
    'src'-folder
    The source directory of the project files needed for building the project frontends
    (files that need to be watched for changes)
    """

    project_src_static_dir: PathLike
    """
    Points to the static directory of the project source files
    """

    project_scripts_dir: PathLike
    """
    Points to the scripts directory of the project source files
    """

    project_src_view_template_dir: PathLike
    """
    The directory where the view templates are stored in the project files src structure
    """

    project_src_view_template_pages_dir: PathLike
    """
    Points to the pages directory of the project view templates
    """

    public_dir: PathLike
    """
    Points to the public folder e.g. "public"
    """

    project_public_dir: PathLike
    """
    Points to the public directory of the project e.g. public/memo
    """

    project_public_static_dir: PathLike
    """
    Points to the public static directory of the project
    """

    project_config_json: PathLike
    """
    Points to the path of the project configuration file
    """

    project_external_config: None | ApplicationExternalConfig
    """
    Contains the external configuration of the project or None if not available
    """

    intern_setup_dir: PathLike
    """
    Points to the internal setup directory
    """

    intern_src_dir: PathLike
    """
    Points to the internal source directory
    """

    intern_template_dir: PathLike
    """
    Always points to the intern view templates (not project files)
    Pointer to the intern view template files (that are copied to the project structure if not available) 
    """

    def __init__(self):
        self.project = None
        self.gams_host = None
        self.project_src_view_template_dir = None
        self.project_files_root = None
        self.intern_template_dir = None
        self.project_src_dir = None
        self.project_src_static_dir = None
        self.project_public_static_dir = None
        self.project_public_dir = None
        self.intern_src_dir = None
        self.public_dir = None
        self.intern_setup_dir = None
        self.project_scripts_dir = None
        self.project_src_view_template_pages_dir = None
        self.project_config_json = None
        self.project_external_config = None

