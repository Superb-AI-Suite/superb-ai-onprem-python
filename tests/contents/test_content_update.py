"""Overwriting an existing content in place (generateContentUpdateURL)."""
import json
from io import BytesIO
from unittest.mock import Mock, patch

import pytest

from spb_onprem import ContentService, DataService
from spb_onprem.base_service import BaseService
from spb_onprem.contents.queries import Queries
from spb_onprem.data.entities import Data
from spb_onprem.exceptions import BadParameterError, BadRequestError
from spb_onprem.users.entities import AuthUser

UPDATE_URL = "https://storage.example.test/bucket/01CONTENT?X-Amz-Signature=deadbeef"


class _Session:
    def __init__(self, status=200):
        self.calls = []
        self.status = status

    def request(self, **kwargs):
        self.calls.append(kwargs)
        response = Mock()
        if self.status >= 400:
            import requests
            response.raise_for_status.side_effect = requests.HTTPError(
                f"{self.status} Client Error: Forbidden for url: {kwargs['url']}"
            )
        else:
            response.raise_for_status.return_value = None
        return response

    def close(self):
        pass


@pytest.fixture
def wired():
    session = _Session()
    with patch.object(BaseService, "requests_retry_session", return_value=session):
        yield session


def _contents():
    service = ContentService()
    service._auth_user = AuthUser(
        host="https://platform.example.test", access_key="k", access_key_secret="s", is_system_sdk=False,
    )
    service.request_gql = Mock(return_value=UPDATE_URL)
    return service


def test_get_update_url_query():
    service = _contents()
    assert service.get_update_url("01CONTENT", "application/json") == UPDATE_URL
    service.request_gql.assert_called_once_with(
        query=Queries.GET_UPDATE_URL, variables={"id": "01CONTENT", "content_type": "application/json"},
    )
    assert "generateContentUpdateURL(id: $id, contentType: $content_type)" in Queries.GET_UPDATE_URL["query"]


def test_get_update_url_needs_an_id():
    with pytest.raises(BadParameterError, match="content_id is required"):
        _contents().get_update_url("")


def test_update_json_content_puts_to_the_same_content_without_credentials(wired):
    service = _contents()

    assert service.update_json_content("01CONTENT", {"objects": [1]}) == "01CONTENT"

    assert service.request_gql.call_args.kwargs["variables"] == {"id": "01CONTENT", "content_type": "application/json"}
    call = wired.calls[0]
    assert call["method"] == "PUT" and call["url"] == UPDATE_URL
    assert call["headers"] == {"Content-Type": "application/json"}  # signed type, no Authorization
    assert json.loads(call["data"]) == {"objects": [1]}


def test_update_content_with_data_and_file(wired, tmp_path):
    service = _contents()
    service.update_content_with_data("01CONTENT", BytesIO(b"abc"), "image/png")
    path = tmp_path / "a.json"
    path.write_text("{}")
    service.update_content("01CONTENT", str(path))

    assert [c["data"] for c in wired.calls] == [b"abc", b"{}"]
    assert [c["headers"]["Content-Type"] for c in wired.calls] == ["image/png", "application/json"]
    assert all("Authorization" not in c["headers"] for c in wired.calls)


@pytest.mark.parametrize("kwargs", [{"content_type": ""}, {"file_data": "text"}])
def test_update_content_with_data_bad_arguments(kwargs):
    args = {"content_id": "01CONTENT", "file_data": b"x", "content_type": "image/png", **kwargs}
    with pytest.raises(BadParameterError):
        _contents().update_content_with_data(**args)


def test_failed_put_hides_the_signature(capsys):
    session = _Session(status=403)
    with patch.object(BaseService, "requests_retry_session", return_value=session):
        with pytest.raises(BadRequestError) as raised:
            _contents().update_json_content("01CONTENT", {})
    output = capsys.readouterr().out + str(raised.value)
    assert "deadbeef" not in output and "01CONTENT?<redacted>" in output


def _data(versions):
    return Data.model_validate({
        "id": "data-1", "datasetId": "d1", "key": "k",
        "slices": [{"id": "s1", "annotation": {"versions": versions}}],
    })


class TestOverwriteSliceAnnotation:
    def _service(self, data):
        service = DataService()
        service.get_data = Mock(return_value=data)
        return service

    def test_overwrites_the_version_content(self):
        service = self._service(_data([{"id": "v1", "content": {"id": "01CONTENT"}}]))
        with patch.object(ContentService, "update_json_content", return_value="01CONTENT") as update:
            assert service.overwrite_slice_annotation_version_content("d1", "data-1", "s1", "v1", {"a": 1}) == "01CONTENT"
        update.assert_called_once_with("01CONTENT", {"a": 1})

    def test_bytes_use_the_given_type(self):
        service = self._service(_data([{"id": "v1", "content": {"id": "01CONTENT"}}]))
        with patch.object(ContentService, "update_content_with_data", return_value="01CONTENT") as update:
            service.overwrite_slice_annotation_version_content("d1", "data-1", "s1", "v1", b"x", "text/plain")
        update.assert_called_once_with("01CONTENT", b"x", "text/plain")

    @pytest.mark.parametrize("versions,slice_id,version_id,message", [
        ([{"id": "v1", "content": {"id": "c"}}], "other", "v1", "is not in slice"),
        ([{"id": "v1", "content": {"id": "c"}}], "s1", "v2", "has no annotation version v2"),
        ([{"id": "v1"}], "s1", "v1", "has no content"),
    ])
    def test_not_found(self, versions, slice_id, version_id, message):
        service = self._service(_data(versions))
        with pytest.raises(BadParameterError, match=message):
            service.overwrite_slice_annotation_version_content("d1", "data-1", slice_id, version_id, {})

    def test_missing_ids(self):
        with pytest.raises(BadParameterError, match="version_id is required"):
            DataService().overwrite_slice_annotation_version_content("d1", "data-1", "s1", None, {})
