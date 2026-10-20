"""Platform credentials go only to the platform API host, never to presigned storage URLs."""
from io import BytesIO
from unittest.mock import Mock, patch

import pytest

from spb_onprem import ContentService, DiagnosisService, ModelService, ReportService
from spb_onprem.base_service import BaseService
from spb_onprem.users.entities import AuthUser

PLATFORM = "https://platform.example.test"
STORAGE_URL = "https://storage.example.test/bucket/key?X-Amz-Signature=abc"


def _user(system: bool) -> AuthUser:
    return AuthUser(
        host=PLATFORM,
        access_key="" if system else "test-key",
        access_key_secret="" if system else "test-secret",
        is_system_sdk=system,
        system_sdk_user_email="system@example.test" if system else None,
    )


class _Session:
    def __init__(self):
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        response = Mock()
        response.raise_for_status.return_value = None
        return response

    def close(self):
        pass


@pytest.fixture(params=[False, True], ids=["access-key", "system"])
def wired(request):
    session = _Session()
    user = _user(request.param)
    with patch.object(BaseService, "requests_retry_session", return_value=session):
        yield session, user


def _service(cls, user):
    service = cls()
    service._auth_user = user
    return service


AUTH_KEYS = {"authorization", "x-user-email"}


def _auth_keys(call):
    return {key.lower() for key in call["headers"]} & AUTH_KEYS


class TestRequest:
    def test_platform_url_gets_credentials(self, wired):
        session, user = wired
        _service(BaseService, user).request("GET", f"{PLATFORM}/api/x", headers={})
        assert _auth_keys(session.calls[0])

    @pytest.mark.parametrize("url", [
        STORAGE_URL,
        "http://platform.example.test/api/x",        # other scheme
        "https://platform.example.test:8443/api/x",  # other port
        "https://platform.example.test.evil/api/x",  # other host
    ])
    def test_other_urls_get_no_credentials(self, wired, url):
        session, user = wired
        _service(BaseService, user).request("GET", url, headers={"Accept": "*/*"})
        assert _auth_keys(session.calls[0]) == set()
        assert session.calls[0]["headers"] == {"Accept": "*/*"}

    def test_default_port_is_the_same_origin(self, wired):
        session, user = wired
        _service(BaseService, user).request("GET", "https://PLATFORM.example.test:443/api/x")
        assert _auth_keys(session.calls[0])

    def test_explicit_auth_flag_wins(self, wired):
        session, user = wired
        service = _service(BaseService, user)
        service.request("PUT", f"{PLATFORM}/upload", auth=False)
        service.request("POST", STORAGE_URL, auth=True)
        assert _auth_keys(session.calls[0]) == set()
        assert _auth_keys(session.calls[1])

    def test_no_headers_argument(self, wired):
        session, user = wired
        _service(BaseService, user).request("GET", STORAGE_URL)
        assert session.calls[0]["headers"] == {}


class TestPresignedUploads:
    """Upload helpers PUT to a presigned URL without platform credentials, even on the platform host."""

    @pytest.mark.parametrize("upload_url", [STORAGE_URL, f"{PLATFORM}/storage/key?X-Amz-Signature=abc"])
    def test_content_uploads(self, wired, tmp_path, upload_url):
        session, user = wired
        service = _service(ContentService, user)
        service.request_gql = Mock(return_value={"uploadURL": upload_url, "content": {"id": "content-1"}})
        file_path = tmp_path / "a.json"
        file_path.write_text("{}")

        service.upload_content(str(file_path), key="a.json")
        service.upload_json_content({"a": 1}, key="a.json")
        service.upload_content_with_data(BytesIO(b"x"), "image/png", key="a.png")

        assert [call["url"] for call in session.calls] == [upload_url] * 3
        assert all(_auth_keys(call) == set() for call in session.calls)

    @pytest.mark.parametrize("cls", [ModelService, DiagnosisService, ReportService])
    def test_json_file_uploads(self, wired, cls):
        session, user = wired
        service = _service(cls, user)
        with patch("spb_onprem.contents.service.ContentService.get_upload_url", return_value=STORAGE_URL):
            service._upload_json_file("01ARZ3NDEKTSV4RRFFQ69G5FAV", "chart.json", {"a": 1})

        assert session.calls[0]["url"] == STORAGE_URL
        assert _auth_keys(session.calls[0]) == set()
