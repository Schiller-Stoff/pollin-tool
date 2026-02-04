import logging
import re
from pathlib import Path
from typing import Set

from pollin.init.ApplicationContext import ApplicationContext


class StaticFileValidator:
    """
    Validates static files (JS, CSS) to ensure no hardcoded project paths are used.
    Since these files are not rendered by Jinja, variables cannot be used.
    Relative paths must be used instead.
    """

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context
        # Define which extensions to check
        self.extensions: Set[str] = {'.js', '.css', '.html', '.xsl', '.sef.json'}

    def validate(self) -> bool:
        logging.info("Starting static file validation...")

        project_abbr = self.app_context.get_config().project
        # Ensure we look in the correct static source directory
        # Adjust 'project_src_static_dir' if your config names it differently
        static_dir = Path(self.app_context.get_config().project_src_static_dir)

        if not static_dir.exists():
            logging.info(f"No static directory found at {static_dir}. Skipping.")
            return True

        # Regex Explanation:
        # 1. (['"\(])       -> Start with a quote or open parenthesis (common in CSS url(...))
        # 2. \s* -> Optional whitespace
        # 3. /              -> Literal root slash
        # 4. (?:pub/)?      -> Optional 'pub/' prefix (matches /pub/memo/ and /memo/)
        # 5. {abbr}         -> The project abbreviation
        # 6. /              -> Must be followed by a slash (prevents matching 'memory')
        pattern_str = f"(['\"\\(])\\s*/(?:pub/)?{re.escape(project_abbr)}/"
        pattern = re.compile(pattern_str)

        has_errors = False

        for file_path in static_dir.rglob("*"):
            if file_path.suffix in self.extensions and file_path.is_file():
                if not self._check_file(file_path, pattern):
                    has_errors = True

        if has_errors:
            logging.error("Static file validation failed! See violations above.")
            return False

        logging.info("Static file validation passed.")
        return True

    def _check_file(self, file_path: Path, pattern: re.Pattern) -> bool:
        try:
            # Read line by line to give precise error locations
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logging.warning(f"Skipping binary or non-utf8 file: {file_path.name}")
            return True

        is_valid = True
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            match = pattern.search(line)
            if match:
                snippet = line.strip()
                if len(snippet) > 60:
                    snippet = snippet[:50] + "..."

                logging.warning(
                    f"Static Violation in {file_path.name} (Line {i}):\n"
                    f"\tFound:   ...{match.group(0)}...\n"
                    f"\tContext: {snippet}\n"
                    f"\tReason:  Hardcoded paths break deployment flexibility and reuse.\n"
                    f"\tFix:     Use POLLIN VARIABLES instead of hardcoded paths."
                )
                is_valid = False

        return is_valid