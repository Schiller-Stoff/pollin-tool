# tests/conftest.py - Simple shared fixtures
import pytest
from unittest.mock import Mock
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

    return project_dir


@pytest.fixture
def sample_object():
    """Create a sample digital object."""
    return DigitalObjectViewModel(
        dc={"title": ["Test Title"], "creator": ["Test Creator"]},
        db={"id": "test.123", "title": "Test Title", "description": "Test desc"},
        props={}
    )


@pytest.fixture
def mock_pyrilo():
    """Simple mock of Pyrilo API client."""
    mock = Mock()
    mock.get_project.return_value = {
        "projectAbbr": "test",
        "description": "Test Project"
    }
    mock.list_objects.return_value = [
        {"id": "test.123", "baseMetadata": {"title": "Test Object"}}
    ]
    mock.get_object.return_value = {
        "id": "test.123",
        "title": "Test Title",
        "description": "Test desc"
    }
    mock.get_dublin_core.return_value = {
        "title": ["Test Title"],
        "creator": ["Test Creator"]
    }
    return mock

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