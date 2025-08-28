import os

from click.testing import CliRunner
from pollin.cli import cli

def test_existence_of_expected_html_output_files(temp_project, mock_api):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(temp_project):
        # Run build command
        result = runner.invoke(cli, ['build', str(temp_project)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # TODO refactor! paths are hardcoded here
        # TODO handle test data (test object, test project etc.) in a better way
        # Check that the output directory and files are created
        assert os.path.exists(temp_project / 'public'), "Public directory not found"
        assert os.path.exists(temp_project / 'public' / 'test'), "Project directory not found"
        assert os.path.exists(temp_project / 'public' / 'test' / 'index.html'), "Index file not found"
        assert os.path.exists(temp_project / 'public' / 'test' / 'objects'), "Objects directory not found"
        assert os.path.exists(temp_project / 'public' / 'test' / 'objects' / 'test.1' / 'index.html'), "Object file not found"

def test_existence_of_expected_static_files(temp_project, mock_api):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(temp_project):
        # Run build command
        result = runner.invoke(cli, ['build', str(temp_project)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # Check that static files are copied
        # TODO harcdoded paths
        assert os.path.exists(temp_project / 'public' / 'test' / 'static'), "Static directory not found"
        assert os.path.exists(temp_project / 'public' / 'test' / 'static' / 'css'), "CSS directory not found"
        assert os.path.exists(temp_project / 'public' / 'test' / 'static' / 'css' / 'styles.css'), "CSS file not found"
        assert os.path.exists(temp_project / 'public' / 'test' / 'static' / 'js'), "JS directory not found"
        assert os.path.exists(temp_project / 'public' / 'test' / 'static' / 'js' / 'scripts.js'), "JS file not found"
        assert os.path.exists(temp_project / 'public' / 'test' / 'static' / 'images'), "Images directory not found"
        assert os.path.exists(temp_project / 'public' / 'test' / 'static' / 'images' / 'logo.png'), "Image file not found"

        assert not os.path.exists(temp_project / 'public' / 'test' / 'static' / 'images' / 'BLA.png'), "Image file exists but should not"