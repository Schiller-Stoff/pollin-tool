from gams_frog.validation.JinjaTemplateValidator import JinjaTemplateValidator
from gams_frog.validation.StaticFileValidator import StaticFileValidator


def test_jinja_valid_files(test_application_context):
    """Test that compliant templates pass validation."""
    template_dir = test_application_context.get_config().project_src_view_template_dir

    # A perfectly good template
    (template_dir / "valid.j2").write_text(
        """
        <a href="{{ context._root_path }}/about">About</a>
        {# This is a comment about /pub/test/ - should be ignored #}
        <span>This project deals with memory and memorials.</span>
        """, encoding="utf-8"
    )

    validator = JinjaTemplateValidator(test_application_context)
    assert validator.validate() is True


def test_jinja_catch_hardcoded_project_path(test_application_context):
    """Test catching /pub/test/ in HTML attributes."""
    template_dir = test_application_context.get_config().project_src_view_template_dir

    # Violation: Hardcoded href
    (template_dir / "violation_1.j2").write_text(
        '<a href="/pub/test/about">Bad Link</a>',
        encoding="utf-8"
    )

    validator = JinjaTemplateValidator(test_application_context)
    assert validator.validate() is False


def test_jinja_catch_hardcoded_variable(test_application_context):
    """Test catching /pub/test/ inside Jinja variables."""
    template_dir = test_application_context.get_config().project_src_view_template_dir

    # Violation: Hardcoded variable
    (template_dir / "violation_2.j2").write_text(
        "{% set my_img = '/pub/test/img/logo.png' %}",
        encoding="utf-8"
    )

    validator = JinjaTemplateValidator(test_application_context)
    assert validator.validate() is False


def test_jinja_ignore_false_positives(test_application_context):
    """Ensure 'testing' or 'testung' does not trigger 'test' detection."""
    template_dir = test_application_context.get_config().project_src_view_template_dir

    (template_dir / "edge_cases.j2").write_text(
        """
        <div class="testing-lane">Content</div>
        <a href="/testung/places">Link</a>
        """,
        encoding="utf-8"
    )

    validator = JinjaTemplateValidator(test_application_context)
    assert validator.validate() is True


def test_jinja_catch_forbidden_origins(test_application_context):
    """Test catching localhost and gams-staging."""
    template_dir = test_application_context.get_config().project_src_view_template_dir

    (template_dir / "origin_violation.j2").write_text(
        '<script src="http://localhost:8080/js/main.js"></script>',
        encoding="utf-8"
    )

    validator = JinjaTemplateValidator(test_application_context)
    assert validator.validate() is False


# --- Static File Validator Tests (Regex) ---

def test_static_valid_files(test_application_context):
    """Test that relative paths in CSS/JS are allowed."""
    static_dir = test_application_context.get_config().project_src_static_dir

    (static_dir / "style.css").write_text(
        """
        .logo { background: url('../img/logo.png'); } 
        /* comment about /pub/memo/ is NOT ignored in regex usually, 
           but our regex requires quotes around it */
        """,
        encoding="utf-8"
    )

    validator = StaticFileValidator(test_application_context)
    assert validator.validate() is True


def test_static_catch_absolute_path(test_application_context):
    """Test catching /pub/test/  in CSS."""
    static_dir = test_application_context.get_config().project_src_static_dir

    (static_dir / "style.css").write_text(
        ".logo { background: url('/pub/test/img/logo.png'); }",
        encoding="utf-8"
    )

    validator = StaticFileValidator(test_application_context)
    assert validator.validate() is False


def test_static_catch_forbidden_origin(test_application_context):
    """Test catching hardcoded API URLs in JS."""
    static_dir = test_application_context.get_config().project_src_static_dir

    (static_dir / "app.js").write_text(
        "const api = 'https://gams.uni-graz.at/archive';",
        encoding="utf-8"
    )

    validator = StaticFileValidator(test_application_context)
    assert validator.validate() is False


def test_static_ignores_binary_files(test_application_context):
    """Ensure the validator doesn't crash on images."""
    static_dir = test_application_context.get_config().project_src_static_dir

    # Create a dummy binary file
    with open(static_dir / "image.png", "wb") as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00')

    validator = StaticFileValidator(test_application_context)
    # Should simply pass (return True) and not crash
    assert validator.validate() is True


def test_static_ignores_excluded_directories(test_application_context):
    """Ensure the validator skips directories like 'lib', 'vendor', and 'node_modules'."""
    static_dir = test_application_context.get_config().project_src_static_dir

    # Create an excluded directory
    lib_dir = static_dir / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)

    # Plant a normally forbidden hardcoded API URL
    (lib_dir / "heavy_library.js").write_text(
        "const api = 'https://gams.uni-graz.at/archive';",
        encoding="utf-8"
    )

    validator = StaticFileValidator(test_application_context)
    # Should pass because 'lib' is in the exclude_dirs set
    assert validator.validate() is True


def test_static_ignores_large_files(test_application_context):
    """Ensure files over the 500KB size limit are skipped entirely."""
    static_dir = test_application_context.get_config().project_src_static_dir

    large_file = static_dir / "massive_dataset.js"

    # Generate 600KB of padding to exceed the 500 * 1024 limit
    padding = "x" * (600 * 1024)

    # Append a forbidden path at the very end
    large_file.write_text(
        f"{padding}\nconst api = 'https://gams.uni-graz.at/archive';",
        encoding="utf-8"
    )

    validator = StaticFileValidator(test_application_context)
    # Should pass because the file size aborts the check before reading
    assert validator.validate() is True


def test_static_ignores_long_lines(test_application_context):
    """Ensure minified code lines (> 5000 chars) are skipped without memory locking."""
    static_dir = test_application_context.get_config().project_src_static_dir

    minified_file = static_dir / "app.min.js"

    # Create a single line longer than 5000 characters containing a forbidden string
    long_line = ("a" * 5001) + " const api = 'https://gams.uni-graz.at/archive'; " + ("b" * 100)

    minified_file.write_text(long_line, encoding="utf-8")

    validator = StaticFileValidator(test_application_context)
    # Should pass because the stream reader skips the abnormally long line
    assert validator.validate() is True
