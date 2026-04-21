"""
Unit tests for ApiProxyHandler.

Uses an in-process aiohttp TestServer as the mocked upstream GAMS5 API plus a second
TestServer running the gams-frog dev app (with the proxy registered) in front of it.
No real network, no gams-frog config — this tests the proxy handler in isolation.

We drive async code via asyncio.run() wrappers rather than adding pytest-asyncio as a
dependency; the test count is small enough that the boilerplate stays bounded.
"""
import asyncio

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from gams_frog.ssr.watch.ApiProxyHandler import ApiProxyHandler


# ---------------------------------------------------------------------------
# Test harness helpers
# ---------------------------------------------------------------------------

def _run(coro):
    """Runs an async test body. Keeps test functions pytest-compatible without pytest-asyncio."""
    return asyncio.run(coro)


def _upstream_origin(server: TestServer) -> str:
    """Returns the http://host:port of a running TestServer (no trailing slash)."""
    return f"http://{server.host}:{server.port}"


def _const(response_factory):
    """Wraps a no-arg response factory into an async aiohttp handler."""
    async def handler(request):
        return response_factory()
    return handler


async def _with_proxy(upstream_app: web.Application, test_body):
    """
    Boots a mocked upstream + a gams-frog dev app with the proxy pointed at it, then runs
    `test_body(client)` where `client` is a TestClient connected to the proxy-fronted app.
    """
    async with TestServer(upstream_app) as upstream:
        gams_frog_app = web.Application()
        ApiProxyHandler(_upstream_origin(upstream)).register(gams_frog_app)

        async with TestServer(gams_frog_app) as gams_frog_server:
            async with TestClient(gams_frog_server) as client:
                await test_body(client)


# ---------------------------------------------------------------------------
# Happy path: GET forwarding
# ---------------------------------------------------------------------------

def test_forwards_get_and_preserves_status_and_json_body():
    async def body(client):
        resp = await client.get("/api/v1/projects/test")
        assert resp.status == 200
        assert await resp.json() == {"projectAbbr": "test"}

    async def run():
        upstream = web.Application()
        upstream.router.add_get(
            "/api/v1/projects/test",
            _const(lambda: web.json_response({"projectAbbr": "test"})),
        )
        await _with_proxy(upstream, body)

    _run(run())


def test_preserves_query_string():
    captured = {}

    async def upstream_handler(request):
        captured["query"] = dict(request.rel_url.query)
        return web.json_response({"ok": True})

    async def body(client):
        resp = await client.get("/api/v1/objects?pageIndex=2&pageSize=50&sortBy=title")
        assert resp.status == 200

    async def run():
        upstream = web.Application()
        upstream.router.add_get("/api/v1/objects", upstream_handler)
        await _with_proxy(upstream, body)

    _run(run())

    assert captured["query"] == {"pageIndex": "2", "pageSize": "50", "sortBy": "title"}


def test_preserves_content_type_header():
    async def body(client):
        resp = await client.get("/api/v1/objects/test.1/datastreams/DC.xml")
        assert resp.status == 200
        assert resp.headers["Content-Type"].startswith("application/xml")
        assert await resp.text() == "<dc><title>t</title></dc>"

    async def run():
        upstream = web.Application()
        upstream.router.add_get(
            "/api/v1/objects/test.1/datastreams/DC.xml",
            _const(lambda: web.Response(
                body=b"<dc><title>t</title></dc>",
                content_type="application/xml",
            )),
        )
        await _with_proxy(upstream, body)

    _run(run())


def test_binary_content_roundtrips_byte_identical():
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 1024 + b"arbitrary binary payload"

    async def body(client):
        resp = await client.get("/api/v1/objects/test.1/datastreams/IMAGE.png/content")
        assert resp.status == 200
        assert await resp.read() == png_bytes

    async def run():
        upstream = web.Application()
        upstream.router.add_get(
            "/api/v1/objects/test.1/datastreams/IMAGE.png/content",
            _const(lambda: web.Response(body=png_bytes, content_type="image/png")),
        )
        await _with_proxy(upstream, body)

    _run(run())


def test_preserves_non_200_status():
    async def body(client):
        resp = await client.get("/api/v1/projects/does-not-exist")
        assert resp.status == 404
        assert "not found" in (await resp.text()).lower()

    async def run():
        upstream = web.Application()
        upstream.router.add_get(
            "/api/v1/projects/does-not-exist",
            _const(lambda: web.Response(status=404, text="Project not found")),
        )
        await _with_proxy(upstream, body)

    _run(run())


# ---------------------------------------------------------------------------
# Header forwarding behavior
# ---------------------------------------------------------------------------

def test_forwards_accept_header_to_upstream():
    captured = {}

    async def upstream_handler(request):
        captured["accept"] = request.headers.get("Accept")
        return web.json_response({})

    async def body(client):
        resp = await client.get(
            "/api/v1/projects/test",
            headers={"Accept": "application/json"},
        )
        assert resp.status == 200

    async def run():
        upstream = web.Application()
        upstream.router.add_get("/api/v1/projects/test", upstream_handler)
        await _with_proxy(upstream, body)

    _run(run())

    assert captured["accept"] == "application/json"


def test_does_not_forward_cookie_header_to_upstream():
    captured = {}

    async def upstream_handler(request):
        captured["cookie"] = request.headers.get("Cookie")
        return web.json_response({})

    async def body(client):
        resp = await client.get(
            "/api/v1/projects/test",
            headers={"Cookie": "JSESSIONID=should-not-reach-upstream"},
        )
        assert resp.status == 200

    async def run():
        upstream = web.Application()
        upstream.router.add_get("/api/v1/projects/test", upstream_handler)
        await _with_proxy(upstream, body)

    _run(run())

    assert captured["cookie"] is None, (
        "Cookie header must not be forwarded — the proxy is read-only/unauthenticated by design"
    )


def test_does_not_pass_set_cookie_from_upstream_to_browser():
    async def upstream_handler(request):
        resp = web.json_response({"ok": True})
        resp.set_cookie("upstream-session", "secret", domain="gams-staging.uni-graz.at")
        return resp

    async def body(client):
        resp = await client.get("/api/v1/projects/test")
        assert resp.status == 200
        # Set-Cookie from upstream must be stripped so we don't accidentally
        # attach staging-domain cookies to localhost.
        assert "Set-Cookie" not in resp.headers

    async def run():
        upstream = web.Application()
        upstream.router.add_get("/api/v1/projects/test", upstream_handler)
        await _with_proxy(upstream, body)

    _run(run())


# ---------------------------------------------------------------------------
# Method restriction — forcing function for auth/CSRF design conversation
# ---------------------------------------------------------------------------

def test_post_returns_405_with_allow_get():
    async def body(client):
        resp = await client.post("/api/v1/projects/test", data=b"x")
        assert resp.status == 405
        assert resp.headers.get("Allow") == "GET"
        text = await resp.text()
        assert "GAMS_FROG PROXY" in text
        assert "GET" in text

    async def run():
        upstream = web.Application()
        # Upstream doesn't even need a POST route — the proxy should reject before forwarding.
        upstream.router.add_get("/api/v1/projects/test", _const(lambda: web.json_response({})))
        await _with_proxy(upstream, body)

    _run(run())


def test_put_patch_delete_all_return_405():
    async def body(client):
        for method in ("put", "patch", "delete"):
            resp = await getattr(client, method)("/api/v1/projects/test")
            assert resp.status == 405, f"{method.upper()} should be rejected"
            assert resp.headers.get("Allow") == "GET"

    async def run():
        upstream = web.Application()
        upstream.router.add_get("/api/v1/projects/test", _const(lambda: web.json_response({})))
        await _with_proxy(upstream, body)

    _run(run())


def test_non_get_does_not_reach_upstream():
    reached = {"upstream": False}

    async def upstream_post(request):
        reached["upstream"] = True
        return web.json_response({})

    async def body(client):
        await client.post("/api/v1/projects/test")

    async def run():
        upstream = web.Application()
        upstream.router.add_post("/api/v1/projects/test", upstream_post)
        upstream.router.add_get("/api/v1/projects/test", _const(lambda: web.json_response({})))
        await _with_proxy(upstream, body)

    _run(run())

    assert reached["upstream"] is False, "Non-GET requests must be rejected before touching upstream"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_unreachable_upstream_returns_502_with_clear_message():
    async def run():
        # Point the proxy at a port nothing is listening on.
        gams_frog_app = web.Application()
        ApiProxyHandler("http://127.0.0.1:1").register(gams_frog_app)

        async with TestServer(gams_frog_app) as gams_frog_server:
            async with TestClient(gams_frog_server) as client:
                resp = await client.get("/api/v1/projects/test")
                assert resp.status == 502
                text = await resp.text()
                assert "GAMS_FROG PROXY ERROR" in text
                assert "127.0.0.1:1" in text

    _run(run())


# ---------------------------------------------------------------------------
# Registration contract
# ---------------------------------------------------------------------------

def test_constructor_rejects_empty_origin():
    import pytest
    with pytest.raises(ValueError):
        ApiProxyHandler("")


def test_constructor_strips_trailing_slash():
    handler = ApiProxyHandler("https://gams-staging.uni-graz.at/")
    assert handler.upstream_origin == "https://gams-staging.uni-graz.at"


def test_register_adds_startup_and_cleanup_hooks():
    app = web.Application()
    # aiohttp.Application ships with a built-in CleanupContext hook on on_startup —
    # capture the baseline so we're asserting on *our* addition, not the total.
    baseline_startup = len(app.on_startup)
    baseline_cleanup = len(app.on_cleanup)

    ApiProxyHandler("http://example.invalid").register(app)

    assert len(app.on_startup) == baseline_startup + 1
    assert len(app.on_cleanup) == baseline_cleanup + 1


def test_non_api_paths_are_not_handled_by_proxy():
    """Paths outside /api/* should not be routed to the proxy handler at all."""
    async def run():
        upstream = web.Application()
        upstream.router.add_get(
            "/api/v1/projects/test", _const(lambda: web.json_response({"api": True}))
        )

        async with TestServer(upstream) as upstream_server:
            gams_frog_app = web.Application()
            ApiProxyHandler(_upstream_origin(upstream_server)).register(gams_frog_app)

            # Non-proxy route to prove the proxy doesn't swallow everything
            gams_frog_app.router.add_get(
                "/static/foo.css", _const(lambda: web.Response(text="body {}"))
            )

            async with TestServer(gams_frog_app) as gams_frog_server:
                async with TestClient(gams_frog_server) as client:
                    api_resp = await client.get("/api/v1/projects/test")
                    assert api_resp.status == 200
                    assert (await api_resp.json()) == {"api": True}

                    static_resp = await client.get("/static/foo.css")
                    assert static_resp.status == 200
                    assert await static_resp.text() == "body {}"

    _run(run())