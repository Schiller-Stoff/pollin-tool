from dataclasses import dataclass


@dataclass
class AppEnv:
    """
    Stores runtime env variables needed in the templates during runtime, e.g. set gams-api host.
    """

    GAMS_API_ORIGIN: str
    PROJECT_ABBR: str

