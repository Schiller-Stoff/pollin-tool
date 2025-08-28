
import pytest
from unittest.mock import Mock, patch
from pollin.common.DigitalObjectViewModel import DigitalObjectViewModel
from pollin.init.ApplicationContext import ApplicationContext
from pollin.init.config.AppEnv import AppEnv
from pollin.init.config.ApplicationConfiguration import ApplicationConfiguration
from pollin.load.ApplicationDatastore import ApplicationDatastore


@pytest.fixture
def temp_project(tmp_path):
    """Create a basic test project structure."""
    project_dir = tmp_path / "test_project"

    # Create directories
    (project_dir / "src" / "templates").mkdir(parents=True)
    (project_dir / "src" / "static").mkdir(parents=True)

    # Create config file
    config = """
        [project]
        projectAbbr = "test"
        
        [dev]
        gamsApiOrigin = "http://localhost:18085"
        
        [build]
        gamsApiOrigin = "http://localhost:18085"
        
        [ui]
        version = "0.0.1"
    """

    (project_dir / "pollin.toml").write_text(config)

    # Create basic templates
    (project_dir / "src" / "templates" / "project.j2").write_text(
        "<h1>{{ project.projectAbbr }}</h1>"
    )
    (project_dir / "src" / "templates" / "object.j2").write_text(
        "<h1>{{ object.db.title }}</h1>"
    )
    (project_dir / "src" / "templates" / "object-list.j2").write_text(
        "<h1>{{ objects[0].title }}</h1>"
    )

    # TODO hardcoded paths
    # Create basic static files
    (project_dir / "src" / "static" / "css" / "styles.css").parent.mkdir(parents=True, exist_ok=True)
    (project_dir / "src" / "static" / "css" / "styles.css").write_text("body { font-family: Arial; }")
    (project_dir / "src" / "static" / "js" / "scripts.js").parent.mkdir(parents=True, exist_ok=True)
    (project_dir / "src" / "static" / "js" / "scripts.js").write_text("console.log('Hello, World!');")
    (project_dir / "src" / "static" / "images" / "logo.png").parent.mkdir(parents=True, exist_ok=True)
    (project_dir / "src" / "static" / "images" / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    return project_dir


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
def test_application_context(temp_project, sample_object):
    """
    Sets up a test application context with test data.

    """

    # Setup mock app context
    app_context = ApplicationContext()

    # TODO refactor
    # Supply config to app context
    config = ApplicationConfiguration(
        project="test",
        gams_host="http://localhost:8080",
        project_files_root=temp_project,
        mode="dev"
    )
    app_context.set_config(config)
    # for config build abb config
    app_context.get_config().ENV = AppEnv(
        GAMS_API_ORIGIN="http://localhost:8080",
        PROJECT_ABBR="test",
        UI_VERSION="1.0.0",
        UI_TITLE="Test Project"
    ) # Initialize with default values

    # mock a datastore with one object
    datastore = ApplicationDatastore()
    datastore.add_object(sample_object)
    datastore.set_project_data({"projectAbbr": "test"})
    app_context.set_app_data_store(datastore)
    return app_context

@pytest.fixture
def mock_api():
    """Simple mock without actual HTTP server."""
    # TODO same procedure for mocking the web server? (to test the dev command)
    # TODO this needs to point to where pyrilo is initiated in the app
    # e.g. pollin.init.AppInitializer.Pyrilo
    with patch('pollin.init.AppInitializer.Pyrilo') as MockPyrilo:

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