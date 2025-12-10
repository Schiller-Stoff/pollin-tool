class DigitalObjectViewModel:
    """
    Model class for the views rendered by jinja2 templates
    """

    db: dict[str, str]
    """
    Object metadata from the database
    """

    props: dict[str, any]
    """
    Search json properties of the object
    """

    # add a to string method
    def __str__(self):
        return f"DigitalObjectViewModel(db={self.db}, props={self.props})"

    def __init__(self, db: dict[str, any], props: dict[str, any]):
        self.db = db
        self.props = props

    def to_dict(self):
        """
        Converts the object to a dictionary
        :return: dictionary representation of the object
        """
        return {
            "db": self.db,
            "props": self.props
        }
