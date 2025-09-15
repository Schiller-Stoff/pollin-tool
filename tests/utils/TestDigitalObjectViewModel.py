from pollin.common.DigitalObjectViewModel import DigitalObjectViewModel
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
        return DigitalObjectViewModel(
            dc=TestDigitalObject.DC,
            db={"id": TestDigitalObject.ID, "title": TestDigitalObject.BASE_METADATA.get("title"), "description": TestDigitalObject.BASE_METADATA.get("description")},
            props={}
        )