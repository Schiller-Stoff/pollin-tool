import logging
import re
from pathlib import Path
from typing import Set

from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from gams_frog.validation.ValidationStatics import ValidationStatics


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
        # excluded folders from validation:
        self.exclude_dirs: Set[str] = {'lib', 'raw'}

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
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in self.exclude_dirs):
                continue
            # skip excluded suffixes
            if file_path.suffix in self.extensions and file_path.is_file():
                if not self._check_file(file_path, pattern):
                    has_errors = True

        if has_errors:
            logging.error("Static file validation failed! See violations above.")
            return False

        logging.info("Static file validation passed.")
        return True

    def _check_file(self, file_path: Path, pattern: re.Pattern) -> bool:
        is_valid = True

        # Fast exit for files over a certain size (e.g., 500KB)
        # Large files are almost certainly datasets or minified bundles.
        if file_path.stat().st_size > 500 * 1024:
            logging.warning(f"StaticFileValidation: Skipping {file_path.name} - file exceeds 500KB size limit.")
            return True

        try:
            # Stream the file instead of file_path.read_text().splitlines()
            with file_path.open("r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    # Skip massive minified lines
                    if len(line) > 5000:
                        logging.warning(f"StaticFileValidation: Skipping line {i} in file {file_path.name} because it exceeds 5000 line.")
                        continue

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
                            f"\tFix:     Use GAMS_FROG VARIABLES instead of hardcoded paths."
                        )
                        is_valid = False

                    # Check 2: Forbidden Origins
                    for origin in ValidationStatics.FORBIDDEN_ORIGINS:
                        if origin in line:
                            logging.warning(
                                f"Static Violation in {file_path.name} (Line {i}):\n"
                                f"\tFound:   ...{origin}...\n"
                                f"\tReason:  Hardcoded paths break deployment flexibility and reuse.\n"
                                f"\tFix:     Use GAMS_FROG VARIABLES instead of hardcoded paths."
                            )
                            is_valid = False
                            break

        except UnicodeDecodeError:
            logging.warning(f"Skipping binary or non-utf8 file for validation: {file_path.name}")
            return True

        return is_valid