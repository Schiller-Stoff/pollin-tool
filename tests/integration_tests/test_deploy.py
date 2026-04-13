import zipfile

from gams_frog.deploy.DeployService import DeployService
from utils.TestDigitalObject import TestDigitalObject
from utils.TestGamsFrogProject import TestPollinProject


# ---------------------------------------------------------------------------
# Integration: deploy after a full build via mock_pollin_env
# ---------------------------------------------------------------------------

class TestDeployAfterBuild:
    """Tests that deploy works correctly with actual build output from mock_pollin_env."""

    def _deploy_after_build(self, mock_pollin_env, mock_gams_auth_client):
        """Helper: sets up app context from a completed build and runs deploy."""
        cli_result, pollin_project = mock_pollin_env
        assert cli_result.exit_code == 0, f"Build failed: {cli_result.output}"

        from gams_frog.ssr.init.ApplicationContext import ApplicationContext
        from gams_frog.ssr.load.ApplicationDatastore import ApplicationDatastore

        app_context = ApplicationContext()
        app_context.set_config(pollin_project.get_config())
        app_context.set_app_data_store(ApplicationDatastore())

        service = DeployService(app_context, mock_gams_auth_client)
        service.deploy()
        return pollin_project

    def _get_uploaded_zip(self, mock_gams_auth_client) -> zipfile.ZipFile:
        """Helper: extracts the zip from the mocked put call and returns an open ZipFile."""
        file_tuple = mock_gams_auth_client.put.call_args[1]["files"]["file"]
        _, buffer, _ = file_tuple
        buffer.seek(0)
        return zipfile.ZipFile(buffer, 'r')

    def test_deploy_after_build_sends_all_output_files(self, mock_gams_frog_env, mock_gams_auth_client):
        """After a successful build, deploy should zip all generated files."""
        self._deploy_after_build(mock_gams_frog_env, mock_gams_auth_client)

        mock_gams_auth_client.put.assert_called_once()
        with self._get_uploaded_zip(mock_gams_auth_client) as zf:
            names = zf.namelist()
            assert "index.html" in names
            assert f"objects/{TestDigitalObject.ID}/index.html" in names
            assert "objects/index.html" in names
            assert "static/css/styles.css" in names
            assert "static/js/scripts.js" in names
            assert "static/images/logo.png" in names

    def test_deploy_zip_contains_no_corrupt_files(self, mock_gams_frog_env, mock_gams_auth_client):
        """The uploaded zip should pass integrity checks."""
        self._deploy_after_build(mock_gams_frog_env, mock_gams_auth_client)

        with self._get_uploaded_zip(mock_gams_auth_client) as zf:
            assert zf.testzip() is None

    def test_deploy_zip_preserves_html_content(self, mock_gams_frog_env, mock_gams_auth_client):
        """Rendered HTML in the zip should contain expected template output."""
        self._deploy_after_build(mock_gams_frog_env, mock_gams_auth_client)

        with self._get_uploaded_zip(mock_gams_auth_client) as zf:
            object_html = zf.read(f"objects/{TestDigitalObject.ID}/index.html").decode("utf-8")
            assert TestDigitalObject.TITLE in object_html

            index_html = zf.read("index.html").decode("utf-8")
            assert TestPollinProject.PROJECT_ABBR in index_html

    def test_deploy_zip_preserves_static_file_content(self, mock_gams_frog_env, mock_gams_auth_client):
        """Static files in the zip should match original source content."""
        self._deploy_after_build(mock_gams_frog_env, mock_gams_auth_client)

        with self._get_uploaded_zip(mock_gams_auth_client) as zf:
            css_content = zf.read("static/css/styles.css").decode("utf-8")
            assert TestPollinProject.TEST_CSS_FILE_CONTENT in css_content

            js_content = zf.read("static/js/scripts.js").decode("utf-8")
            assert TestPollinProject.TEST_JS_FILE_CONTENT in js_content

            logo_bytes = zf.read("static/images/logo.png")
            assert logo_bytes == TestPollinProject.TEST_LOGO_FILE_CONTENT

    def test_deploy_zip_has_no_path_prefixes(self, mock_gams_frog_env, mock_gams_auth_client):
        """No file in the zip should start with 'pub/', 'public/', or '/'."""
        self._deploy_after_build(mock_gams_frog_env, mock_gams_auth_client)

        with self._get_uploaded_zip(mock_gams_auth_client) as zf:
            for name in zf.namelist():
                assert not name.startswith("/"), f"Absolute path: {name}"
                assert not name.startswith("pub/"), f"'pub/' prefix: {name}"
                assert not name.startswith("public/"), f"'public/' prefix: {name}"

    def test_deploy_sends_correct_multipart_metadata(self, mock_gams_frog_env, mock_gams_auth_client):
        """The multipart upload should have the correct filename and content type."""
        self._deploy_after_build(mock_gams_frog_env, mock_gams_auth_client)

        file_tuple = mock_gams_auth_client.put.call_args[1]["files"]["file"]
        filename, _, content_type = file_tuple

        assert filename == f"{TestPollinProject.PROJECT_ABBR}_deploy.zip"
        assert content_type == "application/zip"

    def test_deploy_targets_correct_api_endpoint(self, mock_gams_frog_env, mock_gams_auth_client):
        """deploy() should PUT to v1/projects/{abbr}/web."""
        self._deploy_after_build(mock_gams_frog_env, mock_gams_auth_client)

        endpoint = mock_gams_auth_client.put.call_args[0][0]
        assert endpoint == f"v1/projects/{TestPollinProject.PROJECT_ABBR}/web"