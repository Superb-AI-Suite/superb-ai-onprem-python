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
HEAD_URL = "https://storage.example.test/bucket/01CONTENT?X-Amz-Signature=headsig"


class _Session:
    def __init__(self, status=200, head_status=200):
        self.calls = []
        self.status = status
        self.head_status = head_status

    def request(self, **kwargs):
        self.calls.append(kwargs)
        response = Mock()
        status = self.head_status if kwargs["method"] == "HEAD" else self.status
        if status >= 400:
            import requests
            response.raise_for_status.side_effect = requests.HTTPError(
                f"{status} Client Error: {'Not Found' if status == 404 else 'Forbidden'} for url: {kwargs['url']}"
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
    service.request_gql = Mock(
        side_effect=lambda query, variables: HEAD_URL if query is Queries.GET_HEAD_URL else UPDATE_URL
    )
    return service


def test_get_update_url_query():
    service = _contents()
    assert service.get_update_url("01CONTENT", "application/json") == UPDATE_URL
    service.request_gql.assert_called_once_with(
        query=Queries.GET_UPDATE_URL, variables={"id": "01CONTENT", "content_type": "application/json"},
    )
    assert "generateContentHeadURL(id: $id)" in Queries.GET_HEAD_URL["query"]
    assert "generateContentUpdateURL(id: $id, contentType: $content_type)" in Queries.GET_UPDATE_URL["query"]


def test_get_update_url_needs_an_id():
    with pytest.raises(BadParameterError, match="content_id is required"):
        _contents().get_update_url("")


def test_update_json_content_puts_to_the_same_content_without_credentials(wired):
    service = _contents()

    assert service.update_json_content("01CONTENT", {"objects": [1]}) == "01CONTENT"

    assert service.request_gql.call_args.kwargs["variables"] == {"id": "01CONTENT", "content_type": "application/json"}
    head, call = wired.calls
    assert head["method"] == "HEAD" and head["url"] == HEAD_URL and head["headers"] == {}
    assert call["method"] == "PUT" and call["url"] == UPDATE_URL
    assert call["headers"] == {"Content-Type": "application/json"}  # signed type, no Authorization
    assert json.loads(call["data"]) == {"objects": [1]}


def test_update_content_with_data_and_file(wired, tmp_path):
    service = _contents()
    service.update_content_with_data("01CONTENT", BytesIO(b"abc"), "image/png")
    path = tmp_path / "a.json"
    path.write_text("{}")
    service.update_content("01CONTENT", str(path))

    puts = [c for c in wired.calls if c["method"] == "PUT"]
    assert [c["data"] for c in puts] == [b"abc", b"{}"]
    assert [c["headers"]["Content-Type"] for c in puts] == ["image/png", "application/json"]
    assert all("Authorization" not in c["headers"] for c in wired.calls)


def test_missing_content_is_refused_before_writing():
    """The platform does not check the id; a typo would create a new object."""
    session = _Session(head_status=404)
    with patch.object(BaseService, "requests_retry_session", return_value=session):
        with pytest.raises(BadParameterError, match="does not exist"):
            _contents().update_json_content("01TYPO", {})
    assert [c["method"] for c in session.calls] == ["HEAD"]


def test_check_exists_can_be_turned_off(wired):
    _contents().update_json_content("01CONTENT", {}, check_exists=False)
    assert [c["method"] for c in wired.calls] == ["PUT"]


def test_content_exists():
    for status, expected in ((200, True), (404, False)):
        with patch.object(BaseService, "requests_retry_session", return_value=_Session(head_status=status)):
            assert _contents().content_exists("01CONTENT") is expected
    with patch.object(BaseService, "requests_retry_session", return_value=_Session(head_status=403)):
        with pytest.raises(BadRequestError):
            _contents().content_exists("01CONTENT")


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


@pytest.mark.parametrize("bad", [None, "", "   "])
def test_blank_content_id_sends_nothing(bad):
    service = _contents()
    with patch.object(BaseService, "requests_retry_session", return_value=_Session()) as session:
        with pytest.raises(BadParameterError, match="content_id is required"):
            service.content_exists(bad)
        with pytest.raises(BadParameterError, match="content_id is required"):
            service.update_json_content(bad, {})
    service.request_gql.assert_not_called()
    session.assert_not_called()


@pytest.mark.parametrize("bad", [None, "", "   "])
def test_download_url_needs_a_content_id(bad):
    service = _contents()
    with pytest.raises(BadParameterError, match="content_id is required"):
        service.get_download_url(bad)
    service.request_gql.assert_not_called()
