from utils.TestDigitalObject import TestDigitalObject


class TestDigitalObjectViewModel:
    """
    A utility class holding test data for the digital object view model.
    """

    @staticmethod
    def generate():
        """
        Generate a test DigitalObjectViewModel instance.
        """
        return {
            "id": TestDigitalObject.ID,
            "baseMetadata": TestDigitalObject.BASE_METADATA
        }