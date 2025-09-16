
from click.testing import CliRunner
from pollin.cli import cli

def test_produces_expected_js_file(mock_pollin_env):
    """Integration test for the build command."""

    runner = CliRunner()
    with runner.isolated_filesystem(mock_pollin_env.project_dir):
        # Run build command
        result = runner.invoke(cli, ['build', str(mock_pollin_env.project_dir)])

        assert result.exit_code == 0, f"Build command failed with exit code {result.exit_code} and output: {result.output}"

        # Check that the output files contain expected values
        js_file = mock_pollin_env.get_test_js_path()
        assert js_file.exists(), "Expected JS file not found"
        js_content = js_file.read_text()
        assert mock_pollin_env.TEST_JS_FILE_CONTENT in js_content, "JS file does not contain expected content"