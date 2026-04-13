import logging
import os
import stat
import shutil
from pathlib import Path

from gams_frog.ssr.init.ApplicationContext import ApplicationContext
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

    def _handle_remove_readonly(self, func, path, exc):
        """
        Error handler for shutil.rmtree to fix read-only permission errors.
        It attempts to add write permission and then retries the operation.
        """
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            # If it still fails (e.g. true file lock), we let the exception propagate
            # so the outer retry loop can handle it
            raise

    def refresh(self):
        """
        Refreshes the static files in the public directory.
        Includes robust retry logic for file locking and read-only permissions.
        """

        src_static_dir = self.app_context.get_config().project_src_static_dir
        public_static_dir = self.app_context.get_config().project_public_static_dir

        # Extended retry configuration
        max_retries = 10
        base_wait_time = 0.2

        # Retry logic for Windows file locking and permission issues
        for attempt in range(max_retries):
            try:
                if Path(public_static_dir).exists():
                    # Handle read-only files explicitly using an exception handler
                    # 'onexc' is available in Python 3.12+, which matches the project requirements
                    shutil.rmtree(public_static_dir, onexc=self._handle_remove_readonly)

                shutil.copytree(src_static_dir, public_static_dir)
                logging.info(f"Successfully refreshed static files at {public_static_dir}")
                break  # Success, exit retry loop

            except (PermissionError, OSError) as e:
                if attempt < max_retries - 1:  # Not the last attempt
                    # Progressive delay (e.g., 0.2, 0.4, 0.6 ...)
                    wait_time = base_wait_time * (attempt + 1)
                    logging.warning(
                        f"File system lock/permission issue detected, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logging.error(
                        f"Failed to refresh static files after {max_retries} attempts. Please close any programs (IDEs, terminals) that might be using the files in '{public_static_dir}'. Error: {e}")
                    raise

