import os

from click.testing import CliRunner
from pollin.cli import cli
from utils.TestDigitalObject import TestDigitalObject
from utils.TestProject import TestProject


def test_existence_of_expected_html_output_files(mock_pollin_env):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(mock_pollin_env.project_dir):
        # Run build command
        result = runner.invoke(cli, ['build', str(mock_pollin_env.project_dir)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # Check that the output directory and files are created
        assert os.path.exists(mock_pollin_env.get_config().project_public_dir), "Public directory not found"
        assert os.path.exists(mock_pollin_env.get_config().project_public_static_dir), "Project static directory not found"
        assert os.path.exists(mock_pollin_env.get_config().project_public_dir / 'index.html'), "Index file not found"
        assert os.path.exists(mock_pollin_env.get_config().project_public_dir / 'objects'), "Objects directory not found"
        assert os.path.exists(mock_pollin_env.get_config().project_public_dir / 'objects' / 'test.1' / 'index.html'), "Object file not found"

def test_existence_of_expected_static_files(mock_pollin_env):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(mock_pollin_env.project_dir):
        # Run build command
        result = runner.invoke(cli, ['build', str(mock_pollin_env.project_dir)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # Check that static files are copied
        assert os.path.exists(mock_pollin_env.get_config().project_public_dir), "Public directory not found"
        assert os.path.exists(mock_pollin_env.get_config().project_public_static_dir), "Project static directory not found"
        assert os.path.exists(mock_pollin_env.get_test_css_path()), "CSS file not found"
        assert os.path.exists(mock_pollin_env.get_test_js_path()), "JS file not found"
        assert os.path.exists(mock_pollin_env.get_test_logo_path()), "Logo file not found"

        assert not os.path.exists(mock_pollin_env.get_config().project_public_dir / 'objects' / 'test.123123' / 'index.html'), "Object file should not exist"


def test_build_command_fails_when_invalid_command_is_given(mock_pollin_env):
    """Test the build command with an invalid project path."""
    runner = CliRunner()
    result = runner.invoke(cli, ['build', '/invalid/path/to/project'])

    assert result.exit_code != 0, "Build command should fail with invalid path"
    assert isinstance(result.exception, FileNotFoundError), "Exception should be FileNotFoundError"
    assert "Cannot find required configuration file" in str(result.exception), "Error message should indicate invalid path"


def test_build_command_fails_when_no_command_is_given(mock_pollin_env):
    """Test the build command with no project path."""
    runner = CliRunner()
    result = runner.invoke(cli, ['build'])

    assert result.exit_code != 0, "Build command should fail with no path"
    assert isinstance(result.exception, SystemExit), "Exception should be SystemExit"


def test_build_command_fails_when_no_config_file_was_found_at_path(tmp_path):
    """Test the build command when no config file is present."""
    runner = CliRunner()
    result = runner.invoke(cli, ['build', str(tmp_path)])

    assert result.exit_code != 0, "Build command should fail with no config file"
    assert isinstance(result.exception, FileNotFoundError), "Exception should be FileNotFoundError"
    assert "Cannot find required configuration file" in str(result.exception), "Error message should indicate missing config file"


def test_object_template_contains_expected_values(mock_pollin_env):

    runner = CliRunner()
    with runner.isolated_filesystem(mock_pollin_env.project_dir):
        # Run build command
        result = runner.invoke(cli, ['build', str(mock_pollin_env.project_dir)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        object_html = (mock_pollin_env.get_config().project_public_dir / 'objects' / TestDigitalObject.ID / 'index.html').read_text()
        assert TestDigitalObject.TITLE in object_html, "Object title not found in object HTML"


def test_project_template_contains_expected_values(mock_pollin_env):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(mock_pollin_env.project_dir):
        # Run build command
        result = runner.invoke(cli, ['build', str(mock_pollin_env.project_dir)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # Check that the output files contain expected values
        index_html = (mock_pollin_env.get_config().project_public_dir / 'index.html').read_text()
        assert mock_pollin_env.PROJECT_ABBR in index_html, "Project abbreviation not found in index.html"


def test_object_template_includes_expected_object_to_string(mock_pollin_env):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(mock_pollin_env.project_dir):
        # Run build command
        result = runner.invoke(cli, ['build', str(mock_pollin_env.project_dir)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # Check that the output files contain expected values
        object_html = (mock_pollin_env.get_config().project_public_dir / 'objects' / TestDigitalObject.ID / 'index.html').read_text()
        test_object_to_string = str(TestDigitalObject.generate())
        assert test_object_to_string in object_html, "Object __str__ value not found in object HTML"

def test_project_template_includes_expected_project_to_string(mock_pollin_env):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(mock_pollin_env.project_dir):
        # Run build command
        result = runner.invoke(cli, ['build', str(mock_pollin_env.project_dir)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # Check that the output files contain expected values
        index_html = (mock_pollin_env.get_config().project_public_dir / 'index.html').read_text()
        test_project_to_string = str(TestProject.generate())
        assert test_project_to_string in index_html, "Project __str__ value not found in index.html"


def test_object_list_template_contains_expected_values(mock_pollin_env):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(mock_pollin_env.project_dir):
        # Run build command
        result = runner.invoke(cli, ['build', str(mock_pollin_env.project_dir)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # Check that the output files contain expected values
        object_list_html = (mock_pollin_env.get_config().project_public_dir / 'objects' / 'index.html').read_text()
        assert TestDigitalObject.TITLE in object_list_html, "Object title not found in object list HTML"
        assert TestDigitalObject.ID in object_list_html, "Object ID not found in object list HTML"


def test_object_list_templates_includes_expected_to_string(mock_pollin_env):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(mock_pollin_env.project_dir):
        # Run build command
        result = runner.invoke(cli, ['build', str(mock_pollin_env.project_dir)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # Check that the output files contain expected values
        object_list_html = (mock_pollin_env.get_config().project_public_dir / 'objects' / 'index.html').read_text()
        test_object_to_string = str(TestDigitalObject.generate())
        assert test_object_to_string in object_list_html, "Object __str__ value not found in object list HTML"