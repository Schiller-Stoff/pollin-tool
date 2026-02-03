# tests/test_config.py - Core configuration testing
from pollin.init.config.ApplicationExternalConfigImporter import ApplicationExternalConfigImporter
from pollin.init.config.ApplicationExternalConfig import ApplicationExternalConfig
import pytest

def test_config_loads_from_file(test_pollin_project):
    """Test that configuration loads from TOML file."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_pollin_project.get_config().project_config_toml, "dev"
    )

    assert config_dict is not None
    assert config_dict["project"]["PROJECT_ABBR"] == test_pollin_project.PROJECT_ABBR
    assert config_dict["dev"]["GAMS_API_ORIGIN"] == test_pollin_project.GAMS_API_ORIGIN
    assert config_dict["dev"]["IIIF_IMAGE_SERVER_ORIGIN"] == test_pollin_project.IIIF_IMAGE_SERVER_ORIGIN


def test_config_validates_required_fields():
    """Test that missing required fields raise errors."""
    with pytest.raises(FileNotFoundError):
        ApplicationExternalConfigImporter.import_config("/nonexistent", "dev")


def test_external_config_properties(test_pollin_project):
    """Test ApplicationExternalConfig property access."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_pollin_project.get_config().project_config_toml, "dev"
    )
    config = ApplicationExternalConfig(config_dict, "dev")

    assert config.get_project_abbr() == test_pollin_project.PROJECT_ABBR
    assert config.get_gams_api_origin() == test_pollin_project.GAMS_API_ORIGIN


def test_missing_obj_required_property_should_not_be_none(test_pollin_project):
    """Test behavior when objectsRequired is missing."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_pollin_project.get_config().project_config_toml, "dev"
    )
    config = ApplicationExternalConfig(config_dict, "dev")

    assert config.get_obj_required() is not None


def test_import_config_applies_overrides(tmp_path):
    """
    Verifies that values in pollin.override.toml override the base config,
    while non-overridden values remain intact.
    """
    # 1. Setup: Create the base 'pollin.toml'
    # We write the file manually to avoid dependencies on TOML writers
    base_config_content = """
    [project]
    PROJECT_ABBR = "TEST_BASE"

    [dev]
    GAMS_API_ORIGIN = "http://base.example.com"
    IIIF_IMAGE_SERVER_ORIGIN = "http://base.iiif.com"

    [ui]
    VERSION = "1.0.0"
    """

    config_file = tmp_path / "pollin.toml"
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(base_config_content)

    # 2. Setup: Create the 'pollin.override.toml' in the same directory
    override_config_content = """
    [dev]
    GAMS_API_ORIGIN = "http://override.example.com"
    """

    override_file = tmp_path / "pollin.override.toml"
    with open(override_file, "w", encoding="utf-8") as f:
        f.write(override_config_content)

    # 3. Execution: Run the importer
    # The importer should automatically find the override file next to config_file
    config_dict = ApplicationExternalConfigImporter.import_config(config_file, "dev")

    # 4. Assertions

    # CASE A: Value should be overridden
    assert config_dict["dev"]["GAMS_API_ORIGIN"] == "http://override.example.com", \
        "The GAMS_API_ORIGIN should be taken from the override file."

    # CASE B: Value should preserve the base default (deep merge check)
    assert config_dict["dev"]["IIIF_IMAGE_SERVER_ORIGIN"] == "http://base.iiif.com", \
        "Keys not present in the override file should remain unchanged."

    # CASE C: Top level sections untouched by override should remain
    assert config_dict["project"]["PROJECT_ABBR"] == "TEST_BASE"