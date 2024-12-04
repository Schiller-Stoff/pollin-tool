import shutil
from pathlib import Path

from pollin.System.init.ApplicationContext import ApplicationContext


class ApplicationStaticFileRefresher:
    """
    Refreshes the static files in the public directory
    """

    app_context: ApplicationContext
    """
    The application context
    """

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context

    def refresh(self):
        """
        Refreshes the static files in the public directory
        """

        src_static_dir = self.app_context.get_config().project_src_static_dir
        public_static_dir = self.app_context.get_config().project_public_static_dir

        if Path(public_static_dir).exists():
            # remove the public static directory
            shutil.rmtree(public_static_dir)

        # copy the static directory to the public directory
        shutil.copytree(src_static_dir, public_static_dir)

