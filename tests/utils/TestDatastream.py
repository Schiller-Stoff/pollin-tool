


class TestDatastream:
    """

    """

    DSID = "TEI_SOURCE"
    SIZE = 12345
    TYPE = "Text"
    FILE_NAME = "demo-tei.xml"


    @staticmethod
    def generate():
        """Generate a test digital object dictionary."""
        return {
            "dsid": TestDatastream.DSID,
            "size": TestDatastream.SIZE,
            "fileName": TestDatastream.FILE_NAME,
            "type": TestDatastream.TYPE
        }

    @staticmethod
    def generate_list():
        """
        Generates a list of test datastreams
        """
        return [TestDatastream.generate()]