"""Error paths and redirects against a local HTTP server: no credential leaks.

- 5xx until the retries run out: urllib3 writes the relative URL with its
  query ("Max retries exceeded with url: /bucket/key?X-Amz-Signature=...").
- The raised SDK error has no exception chain, so a traceback (e.g. an Airflow
  task log) does not show the cause's message.
- A system-mode HTTP error does not log the x-user-email header.
- A redirect to another host does not carry x-user-email.
"""
import logging
import threading
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadRequestError, BadRequestParameterError, BadResponseError
from spb_onprem.users.entities import AuthUser

SIGNATURE = "X-Amz-Signature=0123456789abcdef"
EMAIL = "system-user@example.test"


class _Server:
    def __init__(self, handler):
        self.httpd = HTTPServer(("127.0.0.1", 0), handler)
        self.httpd.received = []
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    @property
    def port(self):
        return self.httpd.server_address[1]

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def _handler(status, location=None):
    class Handler(BaseHTTPRequestHandler):
        def _reply(self):
            self.server.received.append({"path": self.path, "headers": dict(self.headers)})
            length = int(self.headers.get("Content-Length") or 0)
            if length:
                self.rfile.read(length)
            self.send_response(status)
            if location:
                self.send_header("Location", location)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"no")

        do_GET = do_PUT = do_POST = _reply

        def log_message(self, *args):  # keep test output clean
            pass

    return Handler


@pytest.fixture
def fast_retries():
    """A real retry session with no backoff, so running out of retries is quick."""
    saved = BaseService._retry_session
    BaseService._retry_session = None
    BaseService.requests_retry_session(retries=2, backoff_factor=0)
    yield
    BaseService._retry_session = saved


def _service(host, system):
    service = BaseService()
    service._auth_user = AuthUser(
        host=host,
        access_key="" if system else "test-key",
        access_key_secret="" if system else "test-secret",
        is_system_sdk=system,
        system_sdk_user_email=EMAIL if system else None,
    )
    service.endpoint = f"{host}/system/graphql/" if system else f"{host}/graphql/"
    return service


def _all_output(capsys, caplog, error):
    captured = capsys.readouterr()
    trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    return captured.out + captured.err + caplog.text + str(error) + trace


def test_retries_exhausted_hides_the_signature(fast_retries, capsys, caplog):
    server = _Server(_handler(500))
    try:
        url = f"http://127.0.0.1:{server.port}/bucket/key?{SIGNATURE}&X-Amz-Date=20261020"
        service = _service("https://platform.example.test", system=False)
        # SDK logs at every level; urllib3's own DEBUG lines (off by default) are not the SDK's.
        with caplog.at_level(logging.DEBUG, logger="spb_onprem"):
            with pytest.raises(BadRequestError) as raised:
                service.request("PUT", url, data=b"x", auth=False)
    finally:
        server.close()

    error = raised.value
    output = _all_output(capsys, caplog, error)
    assert len(server.httpd.received) == 3  # first try + 2 retries
    assert "Max retries exceeded" in output
    assert SIGNATURE not in output
    assert "0123456789abcdef" not in output
    assert error.__cause__ is None and error.__suppress_context__


def test_system_mode_http_error_does_not_log_the_email(fast_retries, capsys, caplog):
    server = _Server(_handler(403))
    try:
        service = _service(f"http://127.0.0.1:{server.port}", system=True)
        with caplog.at_level(logging.DEBUG, logger="spb_onprem"):
            with pytest.raises(BadResponseError) as raised:
                service.request_gql({"name": "x", "query": "query { x }"}, {})
    finally:
        server.close()

    output = _all_output(capsys, caplog, raised.value)
    assert server.httpd.received[0]["headers"].get("x-user-email") == EMAIL  # it was sent to the platform
    assert "Request headers" in output
    assert EMAIL not in output
    assert raised.value.__cause__ is None and raised.value.__suppress_context__


def test_redirect_to_another_host_drops_the_system_header(fast_retries):
    target = _Server(_handler(200))
    redirect = _Server(_handler(307, location=f"http://localhost:{target.port}/elsewhere"))
    try:
        service = _service(f"http://127.0.0.1:{redirect.port}", system=True)
        service.request("GET", f"http://127.0.0.1:{redirect.port}/api/x")
    finally:
        redirect.close()
        target.close()

    assert redirect.httpd.received[0]["headers"].get("x-user-email") == EMAIL
    assert target.httpd.received[0]["path"] == "/elsewhere"
    assert "x-user-email" not in {key.lower() for key in target.httpd.received[0]["headers"]}


@pytest.mark.parametrize("url", [
    "http://localhost:9\\@127.0.0.1:8/x",          # urlsplit and requests disagree on the host
    "http://platform.example.test/x\n",
    "http://platform.example.test:99999/x",        # invalid port
    "http://platform.example.test:abc/x",
])
def test_bad_urls_raise_sdk_errors_without_sending(url, fast_retries):
    service = _service("http://127.0.0.1:8", system=True)
    with pytest.raises(BadRequestParameterError):
        service.request("GET", url)


def test_platform_url_is_judged_like_requests():
    service = _service("http://127.0.0.1:8", system=True)
    assert service.is_platform_url("http://127.0.0.1:8/x")
    assert service.is_platform_url("http://127.0.0.1:8/x?y=1")
    assert not service.is_platform_url("http://127.0.0.1:9/x")


class _DropHandler(BaseHTTPRequestHandler):
    """Closes the connection without an answer, so urllib3 retries with a WARNING."""

    def handle_one_request(self):
        self.server.received.append(self.rfile.readline())
        self.close_connection = True

    def log_message(self, *args):
        pass


def test_urllib3_retry_warnings_hide_the_signature(fast_retries):
    """With logging set up (as in Airflow), urllib3's own WARNING lines must not show the signature."""
    import io

    from spb_onprem.base_service import URLLIB3_URL_LOGGERS

    for name in URLLIB3_URL_LOGGERS:
        assert sum(getattr(f, "spb_redact_url_query", False) for f in logging.getLogger(name).filters) == 1

    root = logging.getLogger()
    saved_handlers, saved_level = root.handlers[:], root.level
    stream = io.StringIO()
    logging.basicConfig(stream=stream, level=logging.WARNING, force=True,
                        format="%(levelname)s %(name)s %(message)s")
    server = _Server(_DropHandler)
    try:
        url = f"http://127.0.0.1:{server.port}/bucket/key?{SIGNATURE}&X-Amz-Date=20261020"
        with pytest.raises(BadRequestError):
            _service("https://platform.example.test", system=False).request("PUT", url, data=b"x", auth=False)
    finally:
        server.close()
        for handler in root.handlers[:]:
            root.removeHandler(handler)
        for handler in saved_handlers:
            root.addHandler(handler)
        root.setLevel(saved_level)

    output = stream.getvalue()
    assert "WARNING urllib3.connectionpool Retrying" in output
    assert "/bucket/key?<redacted>" in output
    assert SIGNATURE not in output and "0123456789abcdef" not in output
