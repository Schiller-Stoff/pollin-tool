import re
from typing import List, Dict
from jinja2.visitor import NodeVisitor

from pollin.web_validation.ValidationStatics import ValidationStatics


class HardcodedPathVisitor(NodeVisitor):
    """
    Jinja2 AST Visitor that inspects text and string literals for forbidden patterns.
    """

    # TODO rename class

    # Centralized configuration for forbidden strings
    FORBIDDEN_ORIGINS = ValidationStatics.FORBIDDEN_ORIGINS

    def __init__(self, project_abbr: str):
        self.project_abbr = project_abbr
        self.errors: List[Dict] = []
        # Pattern explanation:
        # /pub/           -> Match the literal deployment root
        # {abbr}          -> Match the project abbreviation
        # (?=[/'"\s]|$)   -> Lookahead: must be followed by slash, quote, space, or end of line.
        #                    This prevents matching 'memory' if abbr is 'memo',
        #                    but catches '/pub/memo/static' or '/pub/memo"'.
        self.pattern = re.compile(f"/pub/{re.escape(project_abbr)}(?=[/'\"\\s]|$|/)")

    def visit_TemplateData(self, node):
        """Checks raw HTML/text content between Jinja tags."""
        self._check_content(node, node.data)
        self._check_forbidden_origins(node, node.data)

    def visit_Const(self, node):
        """Checks literal values inside Jinja expressions (e.g. {{ "string" }})."""
        if isinstance(node.value, str):
            self._check_content(node, node.value)
            self._check_forbidden_origins(node, node.value)

    # TODO rename function?
    def _check_content(self, node, content: str):
        if self.pattern.search(content):
            # Clean up the snippet for display
            snippet = content.replace('\n', ' ').strip()
            if len(snippet) > 60:
                snippet = snippet[:30] + "..." + snippet[-30:]

            self.errors.append({
                'lineno': node.lineno,
                'snippet': snippet,
                'msg': f"Hardcoded path using the project abbreviation '{self.project_abbr}' is forbidden."
            })

    def _check_forbidden_origins(self, node, content: str):
        """
        TODO write pydoc
        """

        for forbidden_origin in self.FORBIDDEN_ORIGINS:
            if forbidden_origin in content:
                snippet = content.replace('\n', ' ').strip()
                if len(snippet) > 60:
                    snippet = snippet[:30] + "..." + snippet[-30:]

                self.errors.append({
                    'lineno': node.lineno,
                    'snippet': snippet,
                    'msg': f"Using the hardcoded origin {forbidden_origin} is forbidden. Use environment variables instead."
                })
