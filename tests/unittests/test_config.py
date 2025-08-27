# tests/test_config.py - Core configuration testing
from pollin.init.config.ApplicationExternalConfigImporter import ApplicationExternalConfigImporter
from pollin.init.config.ApplicationExternalConfig import ApplicationExternalConfig
import pytest

def test_config_loads_from_file(temp_project):
    """Test that configuration loads from TOML file."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        temp_project / "pollin.toml", "dev"
    )

    assert config_dict is not None
    assert config_dict["project"]["projectAbbr"] == "test"
    assert config_dict["dev"]["gamsApiOrigin"] == "http://localhost:18085"


def test_config_validates_required_fields():
    """Test that missing required fields raise errors."""
    with pytest.raises(FileNotFoundError):
        ApplicationExternalConfigImporter.import_config("/nonexistent", "dev")


def test_external_config_properties(temp_project):
    """Test ApplicationExternalConfig property access."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        temp_project / "pollin.toml", "dev"
    )
    config = ApplicationExternalConfig(config_dict, "dev")

    assert config.get_project_abbr() == "test"
    assert config.get_gams_api_origin() == "http://localhost:18085"


def test_missing_obj_required_property_should_not_be_none(temp_project):
    """Test behavior when objectsRequired is missing."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        temp_project / "pollin.toml", "dev"
    )
    config = ApplicationExternalConfig(config_dict, "dev")

    assert config.get_obj_required() is not None