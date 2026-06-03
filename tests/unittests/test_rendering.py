from gams_frog.ssr.watch.render.DigitalObjectViewRenderer import DigitalObjectViewRenderer
from utils.TestDigitalObject import TestDigitalObject


def test_digital_object_rendering(test_gams_frog_project, test_application_context):
    """Test that digital objects render to HTML files."""

    # Render objects
    renderer = DigitalObjectViewRenderer(test_application_context)
    renderer.render()

    # Check output files exist
    output_dir = test_gams_frog_project.get_config().project_public_dir
    assert (output_dir / "index.html").exists()
    assert (output_dir / "objects" / TestDigitalObject.ID / "index.html").exists()

    # Check content
    object_html = (output_dir / "objects" / TestDigitalObject.ID / "index.html").read_text()
    assert TestDigitalObject.TITLE in object_html


def test_template_error_handling(test_gams_frog_project, test_application_context):
    """Test that template errors are handled gracefully."""
    # Create broken template
    (test_gams_frog_project.get_config().project_src_view_template_dir / "object.j2").write_text(
        "{{ broken.template.syntax }}"
    )

    # Should not crash
    renderer = DigitalObjectViewRenderer(test_application_context)
    renderer.render()

    # Should create error HTML
    error_html = (test_gams_frog_project.get_config().project_public_dir / "objects" / TestDigitalObject.ID / "index.html").read_text()
    assert "GAMS_FROG ERROR" in error_html


def test_asset_helper_rendering(test_gams_frog_project, test_application_context):
    """
    Test that the fn.asset() helper correctly resolves paths via the manifest
    and handles template-relative root paths.
    """
    # 1. Setup: Inject a fake manifest into the render context to simulate
    # the output of the ApplicationStaticFileRenderer step
    render_context = test_application_context.get_application_render_context()
    render_context.set_static_file_hash_mapping({
        'js/scripts.js': 'js/scripts.ab12c3.js'
    })

    # 2. Setup: Create a template that uses our new explicit fn boundary
    template_dir = test_gams_frog_project.get_config().project_src_view_template_dir
    (template_dir / "object.j2").write_text(
        '<script src="{{ fn.asset(\'js/scripts.js\') }}"></script>\n'
        '<link rel="stylesheet" href="{{ fn.asset(\'css/missing.css\') }}">'
    )

    # 3. Execute: Render the digital objects
    renderer = DigitalObjectViewRenderer(test_application_context)
    renderer.render()

    # 4. Verify
    output_dir = test_gams_frog_project.get_config().project_public_dir
    object_html = (output_dir / "objects" / TestDigitalObject.ID / "index.html").read_text()

    # Assertion A: Cache-busting manifest lookup works
    assert "scripts.ab12c3.js" in object_html, "Asset helper failed to use manifest hash"

    # Assertion B: Fallback works when file isn't in manifest (e.g., external or unhashed)
    assert "css/missing.css" in object_html, "Asset helper failed to fallback to original string"

    # Assertion C: The path is correctly prefixed with the static directory and relative path.
    # Note: Depending on your RenderUtils, the relative path from
    # /objects/{TestDigitalObject.ID}/index.html to the root will likely be "../../"
    assert "../../static/js/scripts.ab12c3.js" in object_html or "../static/js/scripts.ab12c3.js" in object_html