
import pytest
from unittest.mock import Mock, patch

from gams_frog.deploy.GamsAuthClient import GamsAuthClient
from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from gams_frog.ssr.load.ApplicationDatastore import ApplicationDatastore
from utils.TestDatastream import TestDatastream
from utils.TestDigitalObject import TestDigitalObject
from utils.TestDigitalObjectViewModel import TestDigitalObjectViewModel
from utils.TestPollinProject import TestPollinProject
from utils.TestProject import TestProject
from click.testing import CliRunner
from gams_frog.cli import cli


@pytest.fixture
def test_pollin_project(tmp_path):
    """Creates a basic testing gams_frog project structure."""
    test_project = TestPollinProject(tmp_path)  # Initialize to create the structure
    return test_project

@pytest.fixture
def test_application_context(test_pollin_project):
    """
    Sets up a test application context with test data.

    """
    # Setup mock app context
    app_context = ApplicationContext()
    app_context.set_config(test_pollin_project.get_config())

    # mock a datastore with one object
    datastore = ApplicationDatastore()
    datastore.add_object(TestDigitalObjectViewModel.generate())
    datastore.set_project_data({"projectAbbr": "test"})
    app_context.set_app_data_store(datastore)
    return app_context

@pytest.fixture
def mock_api():
    """Simple mock without actual HTTP server."""
    with patch('gams_frog.ssr.init.AppInitializer.Pyrilo') as MockPyrilo:

        test_object = TestDigitalObject.generate()
        test_project_dict = TestProject.generate()

        mock = Mock()
        mock.get_project.return_value = test_project_dict
        mock.list_objects.return_value = [test_object]

        mock._collect_objects.return_value = []

        mock.get_object.return_value = test_object

        mock.get_datastream_content.return_value = bytes("Sample datastream content", 'utf-8')

        mock.get_datastreams.return_value = TestDatastream.generate_list()

        # ... other mock responses
        MockPyrilo.return_value = mock
        yield mock

@pytest.fixture
def mock_pollin_env(mock_api, test_pollin_project):
    """
    Sets up a mock Pollin environment with local test project files (as temp files) and mocked GAMS-API.

    """
    # ensure that click is run in isolated filesystem
    runner = CliRunner()
    with runner.isolated_filesystem(test_pollin_project.project_dir):
        # Run build command
        cli_result = runner.invoke(cli, ['build', str(test_pollin_project.project_dir)])
        return cli_result, test_pollin_project



@pytest.fixture
def mock_gams_auth_client():
    """Creates a mock gams_auth_client with a successful default response."""
    client = Mock(spec=GamsAuthClient)
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "projectAbbr": "test",
        "deployedAt": "2026-03-16T12:00:00Z",
        "fileCount": 1,
        "totalSize": 42
    }
    client.put.return_value = response
    return client