from utils.TestProject import TestProject


def test_project_template_includes_expected_project_to_string(mock_pollin_env):
    """Integration test for the build command."""

    cli_result, pollin_project = mock_pollin_env
    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"

    # Check that the output files contain expected values
    index_html = (pollin_project.get_config().project_public_dir / 'index.html').read_text()
    test_project_to_string = str(TestProject.generate())
    assert test_project_to_string in index_html, "Project __str__ value not found in index.html"


def test_project_template_contains_expected_values(mock_pollin_env):
    """Integration test for the build command."""

    cli_result, pollin_project = mock_pollin_env
    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"

    # Check that the output files contain expected values
    index_html = (pollin_project.get_config().project_public_dir / 'index.html').read_text()
    assert pollin_project.PROJECT_ABBR in index_html, "Project abbreviation not found in index.html"