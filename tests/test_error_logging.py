"""Error paths never print or log credentials (#90, merged into 2.0.0)."""
import logging
from unittest.mock import Mock, patch

import pytest
import requests

from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadRequestError, BadResponseError
from spb_onprem.users.entities import AuthUser

SECRET = "Basic dGVzdC1rZXk6dGVzdC1zZWNyZXQ="  # base64 of a test key pair
SIGNATURE = "X-Amz-Signature=deadbeef"


def _http_error(url: str, headers: dict) -> requests.HTTPError:
    response = requests.Response()
    response.status_code = 403
    response.url = url
    response._content = b"forbidden"
    response.request = requests.Request("POST", url, headers=headers).prepare()
    return requests.HTTPError(f"403 Client Error: Forbidden for url: {url}", response=response)


def _service() -> BaseService:
    service = BaseService()
    service._auth_user = AuthUser(
        host="https://platform.example.test", access_key="test-key", access_key_secret="test-secret",
        is_system_sdk=False,
    )
    service.endpoint = "https://platform.example.test/graphql/"
    return service


def _everything(capsys, caplog) -> str:
    captured = capsys.readouterr()
    return captured.out + captured.err + caplog.text


def test_graphql_http_error_hides_credentials(capsys, caplog):
    service = _service()
    session = Mock()
    session.post.return_value.raise_for_status.side_effect = _http_error(
        service.endpoint, {"Authorization": SECRET, "Cookie": "session=abc", "Proxy-Authorization": SECRET},
    )
    session.post.return_value.status_code = 403
    session.post.return_value.elapsed = None

    with caplog.at_level(logging.DEBUG), patch.object(BaseService, "requests_retry_session", return_value=session):
        with pytest.raises(BadResponseError):
            service.request_gql({"name": "x", "query": "query { x }"}, {})

    output = _everything(capsys, caplog)
    assert "Request headers" in output
    assert "<redacted>" in output
    assert SECRET not in output
    assert "session=abc" not in output


def test_presigned_request_error_hides_signature_and_credentials(capsys, caplog):
    service = _service()
    url = f"https://storage.example.test/bucket/key?{SIGNATURE}"
    session = Mock()
    session.request.return_value.raise_for_status.side_effect = _http_error(url, {"Authorization": SECRET})

    with caplog.at_level(logging.DEBUG), patch.object(BaseService, "requests_retry_session", return_value=session):
        with pytest.raises(BadRequestError) as raised:
            service.request("PUT", url, headers={"Content-Type": "application/json"}, auth=False)

    output = _everything(capsys, caplog) + str(raised.value)
    assert SIGNATURE not in output
    assert SECRET not in output
    assert "storage.example.test/bucket/key?<redacted>" in output
    # And no platform credentials were sent to the storage host in the first place.
    sent_headers = session.request.call_args.kwargs["headers"]
    assert "Authorization" not in sent_headers


def test_debug_output_hides_presigned_signatures(capsys, monkeypatch):
    """SDK_DEBUG_GQL=1 prints responses; an uploadURL's signature must not show."""
    monkeypatch.setenv("SDK_DEBUG_GQL", "1")
    service = _service()
    upload_url = f"https://storage.example.test/bucket/key?{SIGNATURE}&X-Amz-Date=20261020"
    session = Mock()
    session.post.return_value.status_code = 200
    session.post.return_value.elapsed = None
    session.post.return_value.raise_for_status.return_value = None
    session.post.return_value.json.return_value = {
        "data": {"createContent": {"uploadURL": upload_url, "content": {"id": "c"}}}
    }

    with patch.object(BaseService, "requests_retry_session", return_value=session):
        result = service.request_gql({"name": "createContent", "query": "mutation { x }"}, {})

    out = capsys.readouterr().out
    assert "SDK_DEBUG_GQL: response_json" in out
    assert "storage.example.test/bucket/key?<redacted>" in out
    assert SIGNATURE not in out
    assert result["uploadURL"] == upload_url  # only the printout is redacted


def test_http_error_body_hides_presigned_signatures(capsys, caplog):
    """The error body (up to 1000 characters) is printed and logged; a URL in it must not show its query."""
    service = _service()
    error = _http_error(service.endpoint, {"Authorization": SECRET})
    error.response._content = f'{{"uploadURL": "https://storage.example.test/k?{SIGNATURE}"}}'.encode()
    session = Mock()
    session.post.return_value.raise_for_status.side_effect = error
    session.post.return_value.status_code = 403
    session.post.return_value.elapsed = None

    with caplog.at_level(logging.DEBUG, logger="spb_onprem"), \
            patch.object(BaseService, "requests_retry_session", return_value=session):
        with pytest.raises(BadResponseError):
            service.request_gql({"name": "x", "query": "query { x }"}, {})

    output = _everything(capsys, caplog)
    assert "storage.example.test/k?<redacted>" in output
    assert SIGNATURE not in output


@pytest.mark.parametrize("url", ["http://a.test:99999/x", "http://a.test:abc/x", "http://a\\@b.test/x", "http://a.test/\x00"])
def test_is_platform_url_raises_sdk_errors(url):
    from spb_onprem.exceptions import BadRequestParameterError

    with pytest.raises(BadRequestParameterError):
        _service().is_platform_url(url)


def test_is_platform_url_location_parse_error(monkeypatch):
    from urllib3.exceptions import LocationParseError

    from spb_onprem import base_service
    from spb_onprem.exceptions import BadRequestParameterError

    def broken(_url):
        raise LocationParseError("bad")

    monkeypatch.setattr(base_service, "parse_url", broken)
    with pytest.raises(BadRequestParameterError):
        _service().is_platform_url("https://platform.example.test/x")
