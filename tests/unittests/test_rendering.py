from pollin.watch.render.DigitalObjectViewRenderer import DigitalObjectViewRenderer

def test_digital_object_rendering(test_project, sample_object, test_application_context):
    """Test that digital objects render to HTML files."""

    # Render objects
    renderer = DigitalObjectViewRenderer(test_application_context)
    renderer.render()

    # Check output files exist
    output_dir = test_project.get_config().project_public_dir
    assert (output_dir / "index.html").exists()
    assert (output_dir / "objects" / "test.123" / "index.html").exists()

    # Check content
    object_html = (output_dir / "objects" / "test.123" / "index.html").read_text()
    assert "Test Title" in object_html


def test_template_error_handling(test_project, sample_object, test_application_context):
    """Test that template errors are handled gracefully."""
    # Create broken template
    (test_project.get_config().project_src_view_template_dir / "object.j2").write_text(
        "{{ broken.template.syntax }}"
    )

    # Should not crash
    renderer = DigitalObjectViewRenderer(test_application_context)
    renderer.render()

    # Should create error HTML
    error_html = (test_project.get_config().project_public_dir / "objects" / "test.123" / "index.html").read_text()
    assert "POLLIN ERROR" in error_html
