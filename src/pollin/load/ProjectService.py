from pollin.init.ApplicationContext import ApplicationContext


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
        return pyrilo.get_project(
            self.app_context.get_config().project
        )