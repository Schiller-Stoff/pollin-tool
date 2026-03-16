import io
import logging
import zipfile
from pathlib import Path

from pollin.deploy.GamsApiClient import GamsApiClient
from pollin.init.ApplicationContext import ApplicationContext


class DeployService:
    """
    Handles deployment of the built static site to the GAMS5 API.

    Zips the contents of the project's public output directory and uploads
    it via PUT /api/v1/projects/{projectAbbr}/web.

    The target API host is determined by the current mode's GAMS_API_ORIGIN:
    - 'stage' deploys to the staging GAMS API
    - 'build' deploys to the production GAMS API

    Requires prior authentication via AuthorizationService, which establishes
    session cookies on the GamsApiClient's requests.Session.
    """

    DEPLOY_API_PATH = "v1/projects/{project_abbr}/web"

    def __init__(self, app_context: ApplicationContext, gams_client: GamsApiClient):
        self.app_context = app_context
        self.gams_client = gams_client

    def _create_zip_buffer(self, source_dir: Path) -> io.BytesIO:
        """
        Creates an in-memory zip archive from the contents of source_dir.
        Files are stored at the zip root (no parent directory prefix).

        :param source_dir: The directory whose contents should be zipped
        :return: BytesIO buffer containing the zip archive
        :raises FileNotFoundError: If source_dir does not exist
        :raises ValueError: If source_dir contains no files
        """
        if not source_dir.exists():
            raise FileNotFoundError(f"Output directory does not exist: {source_dir}")

        buffer = io.BytesIO()
        file_count = 0

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zf.write(file_path, arcname)
                    file_count += 1

        if file_count == 0:
            raise ValueError(f"Output directory is empty, nothing to deploy: {source_dir}")

        buffer.seek(0)
        logging.info(f"Created deployment archive with {file_count} files")
        return buffer

    def _build_deploy_endpoint(self) -> str:
        """
        Constructs the API endpoint path for deployment.
        GamsApiClient prepends the host + /api/ prefix, so we only
        need the path after /api/.
        """
        project_abbr = self.app_context.get_config().project
        return self.DEPLOY_API_PATH.format(project_abbr=project_abbr)

    def deploy(self) -> dict:
        """
        Zips the build output and uploads it to the GAMS5 web deployment endpoint.

        :return: The parsed JSON response from the API (WebDeploymentInfo)
        :raises FileNotFoundError: If the output directory doesn't exist
        :raises ValueError: If the output directory is empty or the API rejects the archive
        :raises ConnectionError: If the API request fails
        :raises PermissionError: If authentication fails
        """
        config = self.app_context.get_config()
        project_abbr = config.project
        source_dir = config.project_public_dir
        mode = config.mode

        logging.info(f"Deploying project '{project_abbr}' from {source_dir} (mode: {mode})")

        # 1. Create zip archive in memory
        zip_buffer = self._create_zip_buffer(source_dir)
        zip_size_mb = zip_buffer.getbuffer().nbytes / (1024 * 1024)
        logging.info(f"Deployment archive size: {zip_size_mb:.2f} MB")

        # 2. Upload via GamsApiClient (multipart file upload)
        endpoint = self._build_deploy_endpoint()
        files = {
            'file': (f"{project_abbr}_deploy.zip", zip_buffer, 'application/zip')
        }

        logging.info(f"Uploading to endpoint: {endpoint}")

        response = self.gams_client.put(
            endpoint,
            files=files,
            raise_errors=False
        )

        # 3. Handle response
        status = response.status_code

        if status == 200:
            result = response.json()
            logging.info(
                f"Deployment successful for project '{project_abbr}'. "
                f"Files: {result.get('fileCount', 'N/A')}, "
                f"Size: {result.get('totalSize', 'N/A')} bytes"
            )
            return result

        elif status in (401, 403):
            raise PermissionError(
                f"Authentication failed for deployment (HTTP {status}). "
                f"Session may have expired."
            )
        elif status == 404:
            raise ConnectionError(
                f"Project '{project_abbr}' not found on GAMS API."
            )
        elif status == 400:
            raise ValueError(
                f"GAMS API rejected the deployment archive (HTTP 400): {response.text}"
            )
        else:
            raise ConnectionError(
                f"Deployment failed (HTTP {status}): {response.text}"
            )