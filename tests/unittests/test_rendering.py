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
    assert "POLLIN ERROR" in error_html
