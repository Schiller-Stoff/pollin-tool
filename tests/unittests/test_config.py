# tests/test_config.py - Core configuration testing
from pollin.init.config.ApplicationExternalConfigImporter import ApplicationExternalConfigImporter
from pollin.init.config.ApplicationExternalConfig import ApplicationExternalConfig
import pytest

def test_config_loads_from_file(test_project):
    """Test that configuration loads from TOML file."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_project.get_config().project_config_toml, "dev"
    )

    assert config_dict is not None
    assert config_dict["project"]["projectAbbr"] == test_project.PROJECT_ABBR
    assert config_dict["dev"]["gamsApiOrigin"] == test_project.GAMS_API_ORIGIN


def test_config_validates_required_fields():
    """Test that missing required fields raise errors."""
    with pytest.raises(FileNotFoundError):
        ApplicationExternalConfigImporter.import_config("/nonexistent", "dev")


def test_external_config_properties(test_project):
    """Test ApplicationExternalConfig property access."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_project.get_config().project_config_toml, "dev"
    )
    config = ApplicationExternalConfig(config_dict, "dev")

    assert config.get_project_abbr() == test_project.PROJECT_ABBR
    assert config.get_gams_api_origin() == test_project.GAMS_API_ORIGIN


def test_missing_obj_required_property_should_not_be_none(test_project):
    """Test behavior when objectsRequired is missing."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_project.get_config().project_config_toml, "dev"
    )
    config = ApplicationExternalConfig(config_dict, "dev")

    assert config.get_obj_required() is not None