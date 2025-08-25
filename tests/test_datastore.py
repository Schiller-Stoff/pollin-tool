# tests/test_datastore.py - Data storage testing
from pollin.System.load.ApplicationDatastore import ApplicationDatastore


def test_datastore_stores_objects(sample_object):
    """Test that datastore can store and retrieve objects."""
    datastore = ApplicationDatastore()

    datastore.add_object(sample_object)
    objects = datastore.get_objects()

    assert len(objects) == 1
    assert objects[0].db["id"] == "test.123"


def test_datastore_finds_object_by_id(sample_object):
    """Test finding objects by ID."""
    datastore = ApplicationDatastore()
    datastore.add_object(sample_object)

    found = datastore.find_object("test.123")
    assert found is not None
    assert found.db["title"] == "Test Title"

    not_found = datastore.find_object("nonexistent")
    assert not_found is None


def test_datastore_stores_project_data():
    """Test storing and retrieving project metadata."""
    datastore = ApplicationDatastore()
    project_data = {"projectAbbr": "test", "description": "Test Project"}

    datastore.set_project_data(project_data)
    retrieved = datastore.get_project_data()

    assert retrieved["projectAbbr"] == "test"
    assert retrieved["description"] == "Test Project"