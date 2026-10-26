"""A plain http:// platform host: a warning when the config is read, a clear error on a redirect.

A server that redirects http to https turns the SDK's GraphQL POST into a GET
(301/302), which then fails with an Apollo CSRF 400 that does not tell why.
Credentials and hosts here are synthetic.
"""
import warnings
from unittest.mock import Mock, patch

import pytest

from spb_onprem.base_service import BaseService, redirect_error
from spb_onprem.exceptions import BadResponseError, InsecureHostWarning
from spb_onprem.users.entities import AuthUser

KEY = "test-key"
SECRET = "test-secret"


@pytest.fixture
def fresh_auth_user():
    """No cached AuthUser, restored afterwards."""
    saved = AuthUser._instance
    AuthUser._instance = None
    yield
    AuthUser._instance = saved


def _config(tmp_path, host):
    path = tmp_path / "onprem-config"
    path.write_text(f"[default]\nhost={host}\naccess_key={KEY}\naccess_key_secret={SECRET}\n")
    return str(path)


def _insecure(record):
    return [item for item in record if issubclass(item.category, InsecureHostWarning)]


class TestHttpHostWarning:
    def test_http_host_warns_once(self, tmp_path, fresh_auth_user):
        path = _config(tmp_path, "http://platform.example.test")
        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            user = AuthUser.get_instance(path)
            assert AuthUser.get_instance(path) is user  # cached: read and warned once

        found = _insecure(record)
        assert len(found) == 1
        message = str(found[0].message)
        assert "uses http://" in message
        assert "https://" in message
        assert path in message
        assert KEY not in message and SECRET not in message
        assert user.host == "http://platform.example.test"  # the host is not changed

    def test_upper_case_scheme_warns(self, tmp_path, fresh_auth_user):
        with pytest.warns(InsecureHostWarning):
            AuthUser.get_instance(_config(tmp_path, "HTTP://platform.example.test:8080"))

    @pytest.mark.parametrize("host", [
        "https://platform.example.test",
        "http://localhost:8088",
        "http://127.0.0.1:8088",
        "http://[::1]:8088",
        "http://app.localhost",
    ])
    def test_https_and_loopback_hosts_do_not_warn(self, host, tmp_path, fresh_auth_user):
        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            AuthUser.get_instance(_config(tmp_path, host))
        assert _insecure(record) == []

    def test_system_sdk_does_not_warn(self, tmp_path, fresh_auth_user, monkeypatch):
        """In the cluster the system SDK talks to the API service over plain http."""
        monkeypatch.setenv("SUNRISE_SERVER_URL", "http://app-api:8080")
        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            user = AuthUser.get_instance(str(tmp_path / "missing-config"))
        assert user.is_system_sdk
        assert _insecure(record) == []


def _redirect(status, location=None):
    response = Mock()
    response.status_code = status
    response.headers = {"Location": location} if location else {}
    response.elapsed = None
    return response


def _service(host):
    service = BaseService()
    service._auth_user = AuthUser(
        host=host, access_key=KEY, access_key_secret=SECRET, is_system_sdk=False, system_sdk_user_email=None,
    )
    service.endpoint = f"{host}/graphql/"
    return service


class TestGraphqlRedirect:
    @pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
    def test_post_is_not_resent(self, status):
        service = _service("http://platform.example.test")
        session = Mock()
        session.post.return_value = _redirect(status, "https://platform.example.test/graphql/")

        with patch.object(BaseService, "requests_retry_session", return_value=session):
            with pytest.raises(BadResponseError, match="Set the host to https://"):
                service.request_gql({"name": "x", "query": "query { x }"}, {})

        session.post.assert_called_once()
        assert session.post.call_args.kwargs["allow_redirects"] is False
        session.post.return_value.json.assert_not_called()

    def test_ok_response_is_unchanged(self):
        service = _service("https://platform.example.test")
        session = Mock()
        session.post.return_value.status_code = 200
        session.post.return_value.elapsed = None
        session.post.return_value.json.return_value = {"data": {"x": 1}}

        with patch.object(BaseService, "requests_retry_session", return_value=session):
            assert service.request_gql({"name": "x", "query": "query { x }"}, {}) == 1


class TestRedirectError:
    def test_http_to_https_names_the_fix(self):
        error = redirect_error("http://platform.example.test/graphql/",
                               _redirect(301, "https://platform.example.test/graphql/"))
        message = str(error)
        assert isinstance(error, BadResponseError)
        assert "HTTP 301 to https://platform.example.test/graphql/" in message
        assert "resent as GET" in message
        assert "Set the host to https://" in message
        assert "~/.spb/onprem-config" in message and "SUNRISE_SERVER_URL" in message

    def test_relative_location_on_the_same_scheme(self):
        message = str(redirect_error("http://platform.example.test/graphql/", _redirect(302, "/login")))
        assert "to http://platform.example.test/login" in message
        assert "Set the host to https://" not in message
        assert "Check the platform host" in message

    def test_location_query_is_hidden(self):
        message = str(redirect_error("https://platform.example.test/graphql/",
                                     _redirect(307, "https://sso.example.test/auth?token=abc123")))
        assert "abc123" not in message
        assert "?<redacted>" in message

    def test_no_location(self):
        message = str(redirect_error("http://platform.example.test/graphql/", _redirect(308)))
        assert "(HTTP 308)" in message
        assert "Check the platform host" in message

    def test_malformed_location(self):
        message = str(redirect_error("http://platform.example.test/graphql/", _redirect(301, "http://[bad")))
        assert "(HTTP 301)" in message
