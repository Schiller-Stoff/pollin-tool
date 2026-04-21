# src/gams_frog/ssr/watch/render/BuildMetadataRenderer.py
import json
import logging
import platform
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from gams_frog.ssr.init.config.ApplicationExternalConfig import ApplicationExternalConfig


class BuildMetadataRenderer:
    """
    Writes a build-metadata JSON file to the project public dir.

    Captures tool version, build environment and a verbatim snapshot of the
    external TOML configuration so sysadmins can audit and reproduce any given
    deployment. Ran as part of `render_views()` so it stays in sync with the
    latest render pass in dev, build and stage modes.
    """

    OUTPUT_FILE_NAME: str = "gams-frog-build.json"
    SCHEMA_VERSION: int = 1
    PACKAGE_NAME: str = "gams-frog"

    app_context: ApplicationContext

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context

    def render(self) -> None:
        """
        Collects metadata and writes it as JSON into `project_public_dir`.
        Failures are logged but must never break the build — this artifact is
        supplementary.
        """
        try:
            metadata = self._collect()
            self._write(metadata)
        except Exception as e:
            logging.warning(f"Failed to write build metadata: {e}")

    def _collect(self) -> dict[str, Any]:
        config = self.app_context.get_config()
        return {
            "schema_version": self.SCHEMA_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "gams_frog": {
                "version": self._tool_version(),
                "python_version": platform.python_version(),
            },
            "build": {
                "mode": config.mode,
                "project_abbr": config.project,
                "gams_host": config.gams_host,
                "output_path": str(config.project_public_dir),
            },
            "config": self._external_config_snapshot(),
        }

    @classmethod
    def _tool_version(cls) -> str:
        try:
            return version(cls.PACKAGE_NAME)
        except PackageNotFoundError:
            return "dev"

    def _external_config_snapshot(self) -> dict[str, Any] | None:
        external = self.app_context.get_config().project_external_config
        if external is None:
            return None
        # ApplicationExternalConfig wraps the raw TOML dict on `.config`.
        # Guard against test fixtures that assign a raw dict directly.
        if isinstance(external, ApplicationExternalConfig):
            return external.config
        if isinstance(external, dict):
            return external
        logging.warning(
            f"Unexpected project_external_config type: {type(external).__name__}; "
            "omitting config section from build metadata."
        )
        return None

    def _write(self, metadata: dict[str, Any]) -> None:
        output_dir: Path = self.app_context.get_config().project_public_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.OUTPUT_FILE_NAME

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

        logging.info(f"Wrote build metadata to {output_path}")