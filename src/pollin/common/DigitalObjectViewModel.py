class DigitalObjectViewModel:
    """
    Model class for the views rendered by jinja2 templates
    """

    db: dict[str, str]
    """
    Object metadata from the database
    """

    # add a to string method
    def __str__(self):
        return f"DigitalObjectViewModel(db={self.db})"

    def __init__(self, db: dict[str, any]):
        self.db = db

    def to_dict(self):
        """
        Converts the object to a dictionary
        :return: dictionary representation of the object
        """
        return {
            "db": self.db
        }
