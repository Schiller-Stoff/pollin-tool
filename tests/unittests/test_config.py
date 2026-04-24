# tests/test_config.py - Core configuration testing
from gams_frog.ssr.init.config.ApplicationExternalConfigImporter import ApplicationExternalConfigImporter
from gams_frog.ssr.init.config.ApplicationExternalConfig import ApplicationExternalConfig
import pytest

def test_config_loads_from_file(test_gams_frog_project):
    """Test that configuration loads from TOML file."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_gams_frog_project.get_config().project_config_toml, "dev"
    )

    assert config_dict is not None
    assert config_dict["project"]["PROJECT_ABBR"] == test_gams_frog_project.PROJECT_ABBR
    assert config_dict["dev"]["GAMS_API_ORIGIN"] == test_gams_frog_project.GAMS_API_ORIGIN
    assert config_dict["dev"]["IIIF_IMAGE_SERVER_ORIGIN"] == test_gams_frog_project.IIIF_IMAGE_SERVER_ORIGIN


def test_config_validates_required_fields():
    """Test that missing required fields raise errors."""
    with pytest.raises(FileNotFoundError):
        ApplicationExternalConfigImporter.import_config("/nonexistent", "dev")


def test_external_config_properties(test_gams_frog_project):
    """Test ApplicationExternalConfig property access."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_gams_frog_project.get_config().project_config_toml, "dev"
    )
    config = ApplicationExternalConfig(config_dict, "dev")

    assert config.get_project_abbr() == test_gams_frog_project.PROJECT_ABBR
    assert config.get_gams_api_origin() == test_gams_frog_project.GAMS_API_ORIGIN


def test_missing_obj_required_property_should_not_be_none(test_gams_frog_project):
    """Test behavior when objectsRequired is missing."""
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_gams_frog_project.get_config().project_config_toml, "dev"
    )
    config = ApplicationExternalConfig(config_dict, "dev")

    assert config.get_obj_required() is not None


def test_import_config_applies_overrides(tmp_path):
    """
    Verifies that values in gams-frog.override.toml override the base config,
    while non-overridden values remain intact.
    """
    # 1. Setup: Create the base 'gams_frog.toml'
    # We write the file manually to avoid dependencies on TOML writers
    base_config_content = """
    [project]
    PROJECT_ABBR = "TEST_BASE"

    [dev]
    GAMS_API_ORIGIN = "http://base.example.com"
    IIIF_IMAGE_SERVER_ORIGIN = "http://base.iiif.com"

    [ui]
    VERSION = "1.0.0"
    
    [dangerous]
    GAMS3_PRODUCTION_ORIGIN = "https://gams.uni-graz.at"
    GAMS5_PRODUCTION_ORIGIN = "https://gams.uni-graz.at"
    """

    config_file = tmp_path / "gams_frog.toml"
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(base_config_content)

    # 2. Setup: Create the 'gams-frog.override.toml' in the same directory
    override_config_content = """
    [dev]
    GAMS_API_ORIGIN = "http://override.example.com"
    """

    override_file = tmp_path / "gams-frog.override.toml"
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


def test_gams_api_protected_origin_fallback(test_gams_frog_project):
    """
    Test that protected origin falls back to the regular GAMS_API_ORIGIN
    when not explicitly specified in the config.
    """
    config_dict = ApplicationExternalConfigImporter.import_config(
        test_gams_frog_project.get_config().project_config_toml, "dev"
    )

    # Ensure the property is NOT in the dictionary
    if "GAMS_API_PROTECTED_ORIGIN" in config_dict["dev"]:
        del config_dict["dev"]["GAMS_API_DEPLOY_ORIGIN"]

    config = ApplicationExternalConfig(config_dict, "dev")

    # The protected origin must equal the standard origin
    assert config.get_gams_api_protected_origin() == config.get_gams_api_origin()


def test_gams_api_deploy_origin_explicit():
    """
    Test that an explicitly set deploy origin overrides the fallback behavior.
    """
    config_dict = {
        "dev": {
            "GAMS_API_ORIGIN": "http://standard-read.example.com",
            "GAMS_API_PROTECTED_ORIGIN": "http://internal-deploy.example.com"
        }
    }
    config = ApplicationExternalConfig(config_dict, "dev")

    # It should return the distinct deploy URL, NOT the standard one
    assert config.get_gams_api_protected_origin() == "http://internal-deploy.example.com"


def test_gams_api_protected_origin_validation():
    """
    Test validation rules for deploy origin (must start with http, no trailing slash).
    """
    config_dict = {
        "dev": {
            "GAMS_API_ORIGIN": "http://standard.example.com",
            "GAMS_API_PROTECTED_ORIGIN": "http://internal-deploy.example.com/"  # Invalid: trailing slash
        }
    }
    config = ApplicationExternalConfig(config_dict, "dev")

    with pytest.raises(ValueError, match="to not have a trailing slash"):
        config.get_gams_api_protected_origin()

    # Test missing HTTP schema
    config_dict["dev"]["GAMS_API_PROTECTED_ORIGIN"] = "ftp://internal-deploy.example.com"
    config_with_bad_schema = ApplicationExternalConfig(config_dict, "dev")

    with pytest.raises(ValueError, match="valid URL starting with 'http'"):
        config_with_bad_schema.get_gams_api_protected_origin()