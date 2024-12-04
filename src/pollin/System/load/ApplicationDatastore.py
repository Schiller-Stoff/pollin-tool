from pollin.System.common.DigitalObjectViewModel import DigitalObjectViewModel


class ApplicationDatastore:
    """
    ApplicationDatastore class is responsible for storing and retrieving application data.
    """

    digital_objects: list[DigitalObjectViewModel] = []
    """
    List of digital objects
    """


    project_data: dict[str, str] = {}
    """
    Project metadata
    """

    def add_object(self, digital_object: DigitalObjectViewModel):
        """
        Adds a digital object to the datastore
        :param digital_object: DigitalObject
        :return:
        """
        self.digital_objects.append(digital_object)

    def get_objects(self) -> list[DigitalObjectViewModel]:
        """
        Returns all digital objects
        :return:
        """
        return self.digital_objects

    def set_objects(self, digital_objects: list[DigitalObjectViewModel]):
        """
        Sets the digital objects
        :param digital_objects: list
        :return:
        """
        self.digital_objects = digital_objects

    def remove_object(self, digital_object: DigitalObjectViewModel):
        """
        Removes a digital object from the datastore
        :param digital_object: DigitalObject
        :return:
        """
        self.digital_objects.remove(digital_object)

    def set_project_data(self, project_data: dict[str, str]):
        """
        Sets the project metadata
        :param project_data: dict
        :return:
        """
        self.project_data = project_data

    def get_project_data(self) -> dict[str, str]:
        """
        Returns the project metadata
        :return:
        """
        return self.project_data







