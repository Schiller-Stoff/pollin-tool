from utils.TestProject import TestProject


class TestDigitalObject:
    """
    A class to generate a test digital object for unit tests.
    """

    PROJECT_ABBR = TestProject.PROJECT_ABBR
    ID = f"{PROJECT_ABBR}.1"
    OBJECT_TYPE = "TEI"
    TITLE = "First Test Object"
    BASE_METADATA = {
        "title": TITLE,
        "description": "A test object for integration testing"
    }
    CREATOR = "Test Creator"

    DC = {
        "title": [BASE_METADATA["title"]],
        "creator": [CREATOR],
        "subject": ["Testing", "Integration"],
        "description": [BASE_METADATA["description"]]
    }

    @staticmethod
    def generate():
        """Generate a test digital object dictionary."""
        return {
            "id": TestDigitalObject.ID,
            "objectType": TestDigitalObject.OBJECT_TYPE,
            "baseMetadata": TestDigitalObject.BASE_METADATA,
            "dc": TestDigitalObject.DC
        }
