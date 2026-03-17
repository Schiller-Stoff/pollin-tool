

class TestProject:
    """Utility class to generate test project data."""

    PROJECT_ABBR = "test"
    DESC = "Test Project Description"

    @staticmethod
    def generate():
        """Generate a test project dictionary."""
        return {
            "projectAbbr": TestProject.PROJECT_ABBR,
            "description": TestProject.DESC
        }