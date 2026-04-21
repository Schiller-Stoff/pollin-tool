import os

from click.testing import CliRunner
from gams_frog.cli import cli
from utils.TestDigitalObject import TestDigitalObject


def test_existence_of_expected_html_output_files(mock_gams_frog_env):
    """Integration test for the build command."""

    cli_result, gams_frog_project = mock_gams_frog_env

    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"

    # Check that the output directory and files are created
    assert os.path.exists(gams_frog_project.get_config().project_public_dir), "Public directory not found"
    assert os.path.exists(gams_frog_project.get_config().project_public_static_dir), "Project static directory not found"
    assert os.path.exists(gams_frog_project.get_config().project_public_dir / 'index.html'), "Index file not found"
    assert os.path.exists(gams_frog_project.get_config().project_public_dir / 'objects'), "Objects directory not found"
    assert os.path.exists(gams_frog_project.get_config().project_public_dir / 'objects' / 'test.1' / 'index.html'), "Object file not found"

def test_existence_of_expected_static_files(mock_gams_frog_env):
    """Integration test for the build command."""

    cli_result, gams_frog_project = mock_gams_frog_env

    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"

    # Check that static files are copied
    assert os.path.exists(gams_frog_project.get_config().project_public_dir), "Public directory not found"
    assert os.path.exists(gams_frog_project.get_config().project_public_static_dir), "Project static directory not found"
    assert os.path.exists(gams_frog_project.get_test_css_path()), "CSS file not found"
    assert os.path.exists(gams_frog_project.get_test_js_path()), "JS file not found"
    assert os.path.exists(gams_frog_project.get_test_logo_path()), "Logo file not found"

    assert not os.path.exists(gams_frog_project.get_config().project_public_dir / 'objects' / 'test.123123' / 'index.html'), "Object file should not exist"


def test_build_command_fails_when_invalid_command_is_given(mock_gams_frog_env):
    """Test the build command with an invalid project path."""
    runner = CliRunner()
    result = runner.invoke(cli, ['build', '/invalid/path/to/project'])

    assert result.exit_code != 0, "Build command should fail with invalid path"
    assert isinstance(result.exception, FileNotFoundError), "Exception should be FileNotFoundError"
    assert "Cannot find required configuration file" in str(result.exception), "Error message should indicate invalid path"


def test_build_command_should_not_fail_when_no_path_was_given(mock_api, test_gams_frog_project):
    """Test that build works when invoked without a path argument (defaults to CWD)."""
    runner = CliRunner()
    original_dir = os.getcwd()
    # i need to make sure that the working directory has the gams_frog.toml from the test files in it
    try:
        os.chdir(test_gams_frog_project.project_dir)
        result = runner.invoke(cli, ['build'])
    finally:
        os.chdir(original_dir)

    assert result.exit_code == 0, f"Build command failed: {result.output}"


def test_build_command_fails_when_no_config_file_was_found_at_path(tmp_path):
    """Test the build command when no config file is present."""
    runner = CliRunner()
    result = runner.invoke(cli, ['build', str(tmp_path)])

    assert result.exit_code != 0, "Build command should fail with no config file"
    assert isinstance(result.exception, FileNotFoundError), "Exception should be FileNotFoundError"
    assert "Cannot find required configuration file" in str(result.exception), "Error message should indicate missing config file"


def test_object_template_contains_expected_values(mock_gams_frog_env):

    cli_result, gams_frog_project = mock_gams_frog_env
    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"

    object_html = (gams_frog_project.get_config().project_public_dir / 'objects' / TestDigitalObject.ID / 'index.html').read_text()
    assert TestDigitalObject.TITLE in object_html, "Object title not found in object HTML"


def test_project_template_contains_expected_values(mock_gams_frog_env):
    """Integration test for the build command."""

    cli_result, gams_frog_project = mock_gams_frog_env
    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"

    # Check that the output files contain expected values
    index_html = (gams_frog_project.get_config().project_public_dir / 'index.html').read_text()
    assert gams_frog_project.PROJECT_ABBR in index_html, "Project abbreviation not found in index.html"


def test_object_template_includes_expected_object_to_string(mock_gams_frog_env):
    """Integration test for the build command."""

    cli_result, gams_frog_project = mock_gams_frog_env
    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"

    # Check that the output files contain expected values
    object_html = (gams_frog_project.get_config().project_public_dir / 'objects' / TestDigitalObject.ID / 'index.html').read_text()
    test_object_to_string = str(TestDigitalObject.generate())
    assert test_object_to_string in object_html, "Object __str__ value not found in object HTML"


def test_object_list_template_contains_expected_values(mock_gams_frog_env):
    """Integration test for the build command."""

    cli_result, gams_frog_project = mock_gams_frog_env

    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"

    # Check that the output files contain expected values
    object_list_html = (gams_frog_project.get_config().project_public_dir / 'objects' / 'index.html').read_text()
    assert TestDigitalObject.TITLE in object_list_html, "Object title not found in object list HTML"
    assert TestDigitalObject.ID in object_list_html, "Object ID not found in object list HTML"


def test_object_list_templates_includes_expected_to_string(mock_gams_frog_env):
    """Integration test for the build command."""

    cli_result, gams_frog_project = mock_gams_frog_env

    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"

    # Check that the output files contain expected values
    object_list_html = (gams_frog_project.get_config().project_public_dir / 'objects' / 'index.html').read_text()
    test_object_to_string = str(TestDigitalObject.generate())
    assert test_object_to_string in object_list_html, "Object __str__ value not found in object list HTML"


def test_build_creates_pub_directory_structure(mock_gams_frog_env):
    cli_result, gams_frog_project = mock_gams_frog_env
    assert cli_result.exit_code == 0

    # public_dir should be just ".../public"
    public_dir = gams_frog_project.get_config().public_dir
    assert public_dir.name == "public"

    # project_public_dir should be ".../public/pub/test"
    project_public_dir = gams_frog_project.get_config().project_public_dir

    assert project_public_dir.exists()
    assert "pub" in project_public_dir.parts[-2]  # Check that 'pub' is the parent of the project folder
    assert (project_public_dir / "index.html").exists()

def test_build_produces_metadata_file(mock_gams_frog_env):
    cli_result, gams_frog_project = mock_gams_frog_env
    assert cli_result.exit_code == 0

    metadata_path = gams_frog_project.get_config().project_public_dir / "gams-frog-build.json"
    assert metadata_path.exists(), "Build metadata file not found"

    import json
    data = json.loads(metadata_path.read_text())
    assert data["build"]["project_abbr"] == gams_frog_project.PROJECT_ABBR