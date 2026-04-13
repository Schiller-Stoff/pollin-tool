import logging
from pathlib import Path

import jinja2

from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from gams_frog.validation.HardcodedPathVisitor import HardcodedPathVisitor


class JinjaTemplateValidator:
    """
    Validates Jinja2 templates using AST parsing to ensure code quality.
    """

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context

    def validate(self) -> bool:
        logging.info("Starting AST-based template validation...")

        project_abbr = self.app_context.get_config().project
        template_dir = self.app_context.get_config().project_src_view_template_dir

        # Create a Jinja environment solely for parsing (no loading/rendering needed)
        env = jinja2.Environment()

        has_errors = False

        # Walk through all .j2 files in the template directory
        for template_path in template_dir.rglob("*.j2"):
            if not self._validate_file(env, template_path, project_abbr):
                has_errors = True

        if has_errors:
            logging.error("Template validation failed! Please fix the hardcoded paths listed above.")
            return False

        logging.info("Template validation passed.")
        return True

    def _validate_file(self, env: jinja2.Environment, file_path: Path, project_abbr: str) -> bool:
        try:
            source = file_path.read_text(encoding="utf-8")

            # Parse the source code into an AST
            # handle_exception=False allows us to catch parsing errors manually if needed
            ast = env.parse(source)

            # Visit the nodes
            visitor = HardcodedPathVisitor(project_abbr)
            visitor.visit(ast)

            if visitor.errors:
                for error in visitor.errors:
                    logging.warning(
                        f"Validation Error in {file_path.name} (Line {error['lineno']}):\n"
                        f"\tReason:  {error['msg']}\n"
                        f"\tContext: \"{error['snippet']}\"\n"
                        f"\tFix:     Use gams-frog variables instead of hardcoded paths."
                    )
                return False

            return True

        except jinja2.TemplateSyntaxError as e:
            # If the template is invalid Jinja, we can't validate code quality, but we should alert.
            logging.error(f"Syntax Error in {file_path.name}: {e}")
            return False
        except Exception as e:
            logging.warning(f"Could not validate file {file_path}: {e}")
            return True  # Don't block build on file IO errors, but log warning