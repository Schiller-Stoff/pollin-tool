from pollin.System.init.ApplicationContext import ApplicationContext


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

        project_metadata = {
            "projectAbbr": "memo",
            "projectTitle": "MEMO",
            "projectSubTitle": "Digitales Memobuch der Stadt Graz",
            "projectDesc": "Das digitale Memobuch der Stadt Graz erinnert an Opfer des Nationalsozialismus und zeigt, wie die Stadt Graz mit ihrer Geschichte umgeht.",
        }

        return project_metadata