from dataclasses import dataclass, asdict


@dataclass
class AppEnv:
    """
    Stores runtime env variables needed in the templates during runtime, e.g. set gams-api host.
    """

    DANGEROUS_GAMS3_PRODUCTION_ORIGIN: str
    DANGEROUS_GAMS5_PRODUCTION_ORIGIN: str

    GAMS_API_ORIGIN: str
    PROJECT_ABBR: str
    UI_VERSION: str
    UI_TITLE: str
    GAMS_FROG_MODE: str
    IIIF_IMAGE_SERVER_ORIGIN: str

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

