
import pytest
from unittest.mock import Mock, patch
from pollin.init.ApplicationContext import ApplicationContext
from pollin.load.ApplicationDatastore import ApplicationDatastore
from utils.TestDigitalObject import TestDigitalObject
from utils.TestDigitalObjectViewModel import TestDigitalObjectViewModel
from utils.TestPollinProject import TestPollinProject
from utils.TestProject import TestProject


@pytest.fixture
def test_project(tmp_path):
    """Creates a basic testing pollin project structure."""
    test_project = TestPollinProject(tmp_path)  # Initialize to create the structure
    return test_project

@pytest.fixture
def test_application_context(test_project):
    """
    Sets up a test application context with test data.

    """
    # Setup mock app context
    app_context = ApplicationContext()
    app_context.set_config(test_project.get_config())

    # mock a datastore with one object
    datastore = ApplicationDatastore()
    datastore.add_object(TestDigitalObjectViewModel.generate())
    datastore.set_project_data({"projectAbbr": "test"})
    app_context.set_app_data_store(datastore)
    return app_context

@pytest.fixture
def mock_api():
    """Simple mock without actual HTTP server."""
    with patch('pollin.init.AppInitializer.Pyrilo') as MockPyrilo:

        test_object = TestDigitalObject.generate()
        test_project_dict = TestProject.generate()

        mock = Mock()
        mock.get_project.return_value = test_project_dict
        mock.list_objects.return_value = [test_object]

        mock._collect_objects.return_value = []

        mock.get_object.return_value = test_object

        mock.get_datastream_content.return_value = bytes("Sample datastream content", 'utf-8')

        # ... other mock responses
        MockPyrilo.return_value = mock
        yield mock

@pytest.fixture
def mock_pollin_env(mock_api, test_project):
    """
    Sets up a mock Pollin environment with local test project files (as temp files) and mocked GAMS-API.

    """
    return test_project