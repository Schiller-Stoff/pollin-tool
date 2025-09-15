
import pytest
from unittest.mock import Mock, patch
from pollin.common.DigitalObjectViewModel import DigitalObjectViewModel
from pollin.init.ApplicationContext import ApplicationContext
from pollin.load.ApplicationDatastore import ApplicationDatastore
from utils.TestPollinProject import TestPollinProject


@pytest.fixture
def test_project(tmp_path):
    """Create a basic test project structure."""
    test_project = TestPollinProject(tmp_path)  # Initialize to create the structure
    return test_project


@pytest.fixture
def sample_object():
    """Create a sample digital object."""
    # TODO hardcoded data
    return DigitalObjectViewModel(
        dc={"title": ["Test Title"], "creator": ["Test Creator"]},
        db={"id": "test.123", "title": "Test Title", "description": "Test desc"},
        props={}
    )

@pytest.fixture
def test_application_context(test_project, sample_object):
    """
    Sets up a test application context with test data.

    """
    # Setup mock app context
    app_context = ApplicationContext()
    app_context.set_config(test_project.get_config())

    # mock a datastore with one object
    datastore = ApplicationDatastore()
    datastore.add_object(sample_object)
    datastore.set_project_data({"projectAbbr": "test"})
    app_context.set_app_data_store(datastore)
    return app_context

@pytest.fixture
def mock_api():
    """Simple mock without actual HTTP server."""
    with patch('pollin.init.AppInitializer.Pyrilo') as MockPyrilo:

        # TODO hardcoded data?
        test_object = {
            "id": "test.1",
            "objectType": "TEI",
            "baseMetadata": {
                "title": "First Test Object",
                "description": "A test object for integration testing"
            },
            "dc": {
                "title": ["First Test Object"],
                "creator": ["Test Creator"],
                "subject": ["Testing", "Integration"],
                "description": ["A test object for integration testing"]
            }
        }

        mock = Mock()
        mock.get_project.return_value = {
            "projectAbbr": "testproj",
            "description": "Integration Test Project Description"
        }
        mock.list_objects.return_value = [
            {
                "id": "test.1",
                "objectType": "TEI",
                "baseMetadata": {
                    "title": "First Test Object",
                    "description": "A test object for integration testing"
                },
                "project": {
                    "projectAbbr": "test"
                },
                "modified": "2023-10-01T12:00:00Z",
                "created": "2023-09-01T12:00:00Z"
            }
        ]

        mock._collect_objects.return_value = []

        mock.get_object.return_value = test_object


        mock.get_datastream_content.return_value = bytes("Sample datastream content", 'utf-8')

        # mock.get_search_json.return_value = {}

        # mock.get_dublin_core.return_value = {}

        # mock.project_modified_since.return_value = False

        # ... other mock responses
        MockPyrilo.return_value = mock
        yield mock