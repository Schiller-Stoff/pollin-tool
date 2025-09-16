
def test_produces_expected_js_file(mock_pollin_env):
    """Integration test for the build command."""
    cli_result, pollin_project = mock_pollin_env
    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"
    # Check that the output files contain expected values
    js_file = pollin_project.get_test_js_path()
    assert js_file.exists(), "Expected JS file not found"
    js_content = js_file.read_text()
    assert pollin_project.TEST_JS_FILE_CONTENT in js_content, "JS file does not contain expected content"
