import hashlib
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

                # hashing logic
                manifest = self._copy_and_hash_static_files(src_static_dir, public_static_dir)

                # Attach the manifest to the app_context so the template renderer can access it.
                # (You don't necessarily need to pre-define this in ApplicationContext,
                # Python allows dynamic attribute assignment, though defining it is cleaner).
                self.app_context.get_application_render_context().set_static_file_hash_mapping(manifest)

                # self.app_context.asset_manifest = manifest
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

    def _copy_and_hash_static_files(self, src_dir: Path, dest_dir: Path) -> dict:
        manifest = {}

        mode = self.app_context.get_config().mode
        is_dev = mode == "dev"
        dev_timestamp = str(int(time.time()))

        # Define which folders should NEVER be hashed (relative to src/static)
        # We use a set for fast O(1) lookups
        excluded_folders = {"lib", "raw"}

        for root, _, files in os.walk(src_dir):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(src_dir)
                manifest_key = str(rel_path).replace(os.sep, '/')

                # Check if the file is inside one of our excluded folders
                # rel_path.parts gives us a tuple of the path segments (e.g., ('vendor', 'jquery.js'))
                is_vendor_file = len(rel_path.parts) > 0 and rel_path.parts[0] in excluded_folders

                if is_vendor_file:
                # TODO enable again skipping in dev?
                # if is_dev or is_vendor_file:
                    # BYPASS HASHING:
                    # Triggers if we are in dev mode OR if it's a 3rd-party vendor file
                    target_file_path = dest_dir / rel_path
                    target_file_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, target_file_path)

                    if is_dev and not is_vendor_file:
                        # Append query string for dev-mode cache busting on our own files
                        manifest[manifest_key] = f"{manifest_key}?v={dev_timestamp}"
                    else:
                        # Vendor files get mapped exactly 1:1, no query strings, no hashes
                        manifest[manifest_key] = manifest_key

                else:
                    # PRODUCTION HASHING for your actual app code
                    hasher = hashlib.md5()
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
                    file_hash = hasher.hexdigest()[:8]

                    new_filename = f"{file_path.stem}.{file_hash}{file_path.suffix}"
                    new_rel_path = rel_path.with_name(new_filename)

                    target_file_path = dest_dir / new_rel_path
                    target_file_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, target_file_path)

                    manifest[manifest_key] = str(new_rel_path).replace(os.sep, '/')

        return manifest