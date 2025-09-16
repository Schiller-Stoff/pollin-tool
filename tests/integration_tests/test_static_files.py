
def test_produces_expected_js_file(mock_pollin_env):
    cli_result, pollin_project = mock_pollin_env
    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"
    # Check that the output files contain expected values
    js_file = pollin_project.get_test_js_path()
    assert js_file.exists(), "Expected JS file not found"
    js_content = js_file.read_text()
    assert pollin_project.TEST_JS_FILE_CONTENT in js_content, "JS file does not contain expected content"

def test_produces_expected_css_file(mock_pollin_env):
    cli_result, pollin_project = mock_pollin_env
    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"
    # Check that the output files contain expected values
    css_file = pollin_project.get_test_css_path()
    assert css_file.exists(), "Expected CSS file not found"
    css_content = css_file.read_text()
    assert pollin_project.TEST_CSS_FILE_CONTENT in css_content, "CSS file does not contain expected content"

def test_produces_expected_image_file(mock_pollin_env):
    cli_result, pollin_project = mock_pollin_env
    assert cli_result.exit_code == 0, f"Build command failed with exit code {cli_result.exit_code} and output: {cli_result.output}"
    # Check that the output files contain expected values
    image_file = pollin_project.get_test_logo_path()
    assert image_file.exists(), "Expected image file not found"
    image_content = image_file.read_bytes()
    assert image_content == pollin_project.TEST_LOGO_FILE_CONTENT, "Image file does not contain expected content"