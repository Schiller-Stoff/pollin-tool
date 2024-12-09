from pollin.System.init.ApplicationContext import ApplicationContext
import tomllib


class ProjectService:
    """
    ProjectService class is responsible for loading GAMS project data

    """

    app_context: ApplicationContext

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context


    def load(self):
        """
        Loads GAMS project data
        """
        pyrilo = self.app_context.get_pyrilo()

        project_metadata = self.read_project_toml()
        return project_metadata

    def read_project_toml(self):
        """
        Reads the project.toml file with the project metadata
            projectAbbr = "<the project abbreviation>"
            projectTitle = "<the project title>"
            projectSubTitle = "<the project subtitle>"
            projectDesc = "<the project description>"

        """
        with open('project.toml', 'rb') as file:
            try:
                project_metadata = tomllib.load(file)
            except tomllib.TOMLDecodeError as e:
                print(f"Error decoding project metadata: {e}")
                project_metadata = None
        return project_metadata
