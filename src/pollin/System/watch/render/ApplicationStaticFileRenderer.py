import logging
import shutil
from pathlib import Path

from pollin.System.init.ApplicationContext import ApplicationContext
import time

class ApplicationStaticFileRenderer:
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

        # Retry logic for Windows file locking
        for attempt in range(3):
            try:
                if Path(public_static_dir).exists():
                    shutil.rmtree(public_static_dir)
                shutil.copytree(src_static_dir, public_static_dir)
                break  # Success, exit retry loop
            except PermissionError as e:
                if attempt < 2:  # Not the last attempt
                    logging.warning(f"File lock detected, retrying... (attempt {attempt + 1})")
                    time.sleep(0.1 * (attempt + 1))  # Progressive delay
                else:
                    logging.error(f"Failed to refresh static files after 3 attempts: {e}")
                    raise

