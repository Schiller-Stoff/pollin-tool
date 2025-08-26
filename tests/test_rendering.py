# tests/test_rendering.py - Core rendering functionality

from pollin.System.init.config.AppEnv import AppEnv
from pollin.System.init.config.ApplicationConfiguration import ApplicationConfiguration
from pollin.System.load.ApplicationDatastore import ApplicationDatastore
from pollin.System.watch.render.DigitalObjectViewRenderer import DigitalObjectViewRenderer
from pollin.System.init.ApplicationContext import ApplicationContext


def test_digital_object_rendering(temp_project, sample_object):
    """Test that digital objects render to HTML files."""
    # Setup mock app context
    app_context = ApplicationContext()

    # TODO always supply the same mock / test data
    # TODO refactor
    # Supply config to app context
    config = ApplicationConfiguration(
        project="test",
        gams_host="http://localhost:8080",
        project_files_root=temp_project
    )
    app_context.set_config(config)
    # for config build abb config
    app_context.get_config().ENV = AppEnv(
        GAMS_API_ORIGIN="http://localhost:8080",
        PROJECT_ABBR="test",
        UI_VERSION="1.0.0",
        UI_TITLE="Test Project"
    ) # Initialize with default values

    # mock a datastore with one object
    datastore = ApplicationDatastore()
    datastore.add_object(sample_object)
    datastore.set_project_data({"projectAbbr": "test"})
    app_context.set_app_data_store(datastore)

    # Render objects
    renderer = DigitalObjectViewRenderer(app_context)
    renderer.render()

    # Check output files exist
    output_dir = temp_project / "public" / "test"
    assert (output_dir / "index.html").exists()
    assert (output_dir / "objects" / "test.123" / "index.html").exists()

    # Check content
    object_html = (output_dir / "objects" / "test.123" / "index.html").read_text()
    assert "Test Title" in object_html


def test_template_error_handling(temp_project, sample_object):
    """Test that template errors are handled gracefully."""
    # Create broken template
    (temp_project / "src" / "templates" / "object.j2").write_text(
        "{{ broken.template.syntax }}"
    )

    # TODO always supply the same mock / test data
    app_context = ApplicationContext()
    config = ApplicationConfiguration(
        project="test",
        gams_host="http://localhost",
        project_files_root=temp_project
    )
    app_context.set_config(config)

    datastore = ApplicationDatastore()
    datastore.add_object(sample_object)
    app_context.set_app_data_store(datastore)

    # Should not crash
    renderer = DigitalObjectViewRenderer(app_context)
    renderer.render()

    # Should create error HTML
    error_html = (temp_project / "public" / "test" / "objects" / "test.123" / "index.html").read_text()
    assert "POLLIN ERROR" in error_html
