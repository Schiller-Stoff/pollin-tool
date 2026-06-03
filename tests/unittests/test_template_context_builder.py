
from gams_frog.ssr.watch.render.ApplicationTemplateContextBuilder import ApplicationTemplateContextBuilder


def test_builder_creates_base_structure(test_application_context):
    """Test that the builder creates the strict context/fn namespace and injects base framework data."""
    builder = ApplicationTemplateContextBuilder(test_application_context)

    # Execute
    payload = builder.create(template_name="object-list.j2", root_path="../../")

    # Verify top-level namespaces
    assert "context" in payload
    assert "fn" in payload
    assert callable(payload["fn"]["asset"]), "asset should be a callable function"

    # Verify base context data
    ctx = payload["context"]
    assert ctx["_template_name"] == "object-list", "Should strip the .j2 extension"
    assert ctx["_template_file_name"] == "object-list.j2"
    assert ctx["_root_path"] == "../../"
    assert "project" in ctx, "Project metadata must be injected"
    assert "env" in ctx, "Environment config must be injected"
    assert "manifest" in ctx, "Manifest must be injected"


def test_builder_injects_extra_context(test_application_context):
    """Test that page-specific data (like objects) is properly merged into the context."""
    builder = ApplicationTemplateContextBuilder(test_application_context)

    # Mock some extra data
    extra_data = {
        "object": {"id": "test:1", "title": "Test Object"},
        "custom_flag": True
    }

    # Execute
    payload = builder.create(template_name="object.j2", root_path="../", extra_context=extra_data)

    # Verify
    ctx = payload["context"]
    assert ctx["object"]["id"] == "test:1", "Extra context 'object' was not merged"
    assert ctx["custom_flag"] is True, "Extra context 'custom_flag' was not merged"

    # Ensure it didn't overwrite core fields unexpectedly
    assert ctx["_template_name"] == "object"


def test_asset_helper_resolution_logic(test_application_context):
    """Test the internal logic of the asset_helper closure (manifest lookup, external URLs, pathing)."""
    # 1. Setup: Inject a fake manifest into the application context
    render_ctx = test_application_context.get_application_render_context()
    render_ctx.set_static_file_hash_mapping({
        'js/app.js': 'js/app.987654.js',
        'css/main.css': 'css/main.123456.css'
    })

    builder = ApplicationTemplateContextBuilder(test_application_context)

    # Execute: Create payload with a specific root path
    payload = builder.create(template_name="index.j2", root_path="../../")
    asset = payload["fn"]["asset"]

    # Scenario A: External URLs should be bypassed entirely
    assert asset("https://cdn.example.com/vue.js") == "https://cdn.example.com/vue.js"
    assert asset("http://fonts.com/robot") == "http://fonts.com/robot"
    assert asset("//cdnjs.cloudflare.com/lib.js") == "//cdnjs.cloudflare.com/lib.js"

    # Scenario B: Known files should be resolved using the manifest hash
    assert asset("js/app.js") == "../../static/js/app.987654.js"

    # Scenario C: Unknown/unhashed files should fallback gracefully
    assert asset("img/logo.png") == "../../static/img/logo.png"

    # Scenario D: Accidental leading slashes should be cleaned up
    # If the user passes "/img/logo.png", it should not resolve to "../../static//img/logo.png"
    assert asset("/img/logo.png") == "../../static/img/logo.png"


def test_asset_helper_handles_empty_root_path(test_application_context):
    """Test edge cases with the root_path string manipulations."""
    builder = ApplicationTemplateContextBuilder(test_application_context)

    # Execute with an empty root path (e.g., rendering the root index.html)
    payload = builder.create(template_name="index.j2", root_path="")
    asset = payload["fn"]["asset"]

    # Expected: empty root path + static -> "/static/file" or "static/file"
    # Given the implementation `base_path = root_path.rstrip('/')`, `""` becomes `""`
    # `f"{base_path}/static/..."` -> `/static/js/script.js`
    assert asset("js/script.js") == "/static/js/script.js"