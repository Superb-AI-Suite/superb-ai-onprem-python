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
