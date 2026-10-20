"""invoke_model_deployment: multipart request, multipart response, relay errors (C4, C8, C11)."""
import json
from unittest.mock import Mock, patch

import pytest
import requests

from spb_onprem import (
    DeploymentInvokeError,
    DeploymentInvokeFile,
    DeploymentInvokeRequest,
    ModelDeploymentService,
)
from spb_onprem.exceptions import (
    BadParameterError,
    BadResponseError,
    ConflictError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
    UnknownError,
)
from spb_onprem.model_deployments import invoke as invoke_module
from spb_onprem.model_deployments.invoke import parse_multipart
from spb_onprem.model_deployments.service import DEFAULT_INVOKE_TIMEOUT
from spb_onprem.users.entities import AuthUser

HOST = "https://platform.example.test"
BOUNDARY = "b1f0"
# Binary bytes that look like line ends and a delimiter without the boundary.
VIDEO = b"\x00\x01\r\n--b1\r\n\r\n\xff\xfe" * 100


def _multipart(parts, boundary=BOUNDARY, preamble=b""):
    body = preamble
    for name, filename, content_type, data in parts:
        disposition = f'form-data; name="{name}"' + (f'; filename="{filename}"' if filename else "")
        body += f"--{boundary}\r\nContent-Disposition: {disposition}\r\n".encode()
        if content_type:
            body += f"Content-Type: {content_type}\r\n".encode()
        body += b"\r\n" + data + b"\r\n"
    return body + f"--{boundary}--\r\n".encode()


def _response(status=200, body=b"", content_type=None, headers=None):
    response = Mock()
    response.status_code = status
    response.content = body
    response.headers = {**({"Content-Type": content_type} if content_type else {}), **(headers or {})}
    return response


def _service(system=False):
    service = ModelDeploymentService()
    service._auth_user = AuthUser(
        host=HOST + "/",
        access_key="" if system else "test-key",
        access_key_secret="" if system else "test-secret",
        is_system_sdk=system,
        system_sdk_user_email="system@example.test" if system else None,
    )
    return service


def _call(response, request=None, **kwargs):
    service = _service()
    with patch("spb_onprem.model_deployments.service.requests.post", return_value=response) as post:
        result = service.invoke_model_deployment(
            "dataset 1", "01JDEPLOY", request or DeploymentInvokeRequest(text="hi"), **kwargs
        )
    return result, post


class TestRequest:
    def test_parts_in_contract_order(self, tmp_path):
        image = tmp_path / "frame.png"
        image.write_bytes(b"\x89PNG")
        request = DeploymentInvokeRequest(
            video=DeploymentInvokeFile.from_bytes(VIDEO, "clip.mp4"),
            image=[str(image)],
            json={"seed": 7},
            text=["first", "second"],
            file=DeploymentInvokeFile.from_bytes(b"a,b", "table.csv", content_type="text/csv"),
        )

        files = request.multipart_files()

        assert [(name, value[0], value[2]) for name, value in files] == [
            ("text", None, "text/plain; charset=utf-8"),
            ("text", None, "text/plain; charset=utf-8"),
            ("json", None, "application/json"),
            ("image", "frame.png", "image/png"),
            ("video", "clip.mp4", "video/mp4"),
            ("file", "table.csv", "text/csv"),
        ]
        assert files[2][1][1] == b'{"seed": 7}'
        assert files[3][1][1] == b"\x89PNG"
        assert files[4][1][1] == VIDEO

    def test_requests_encoding_round_trips_through_the_parser(self):
        request = DeploymentInvokeRequest(text="한국어 prompt", json=['{"steps": 4}'],
                                          video=DeploymentInvokeFile.from_bytes(VIDEO, "clip.mp4"))
        prepared = requests.Request("POST", HOST, files=request.multipart_files()).prepare()

        parts = parse_multipart(prepared.headers["Content-Type"], prepared.body)

        assert [(p.name, p.filename) for p in parts] == [("text", None), ("json", None), ("video", "clip.mp4")]
        assert parts[0].text == "한국어 prompt"
        assert parts[1].json() == {"steps": 4}
        assert parts[2].data == VIDEO

    @pytest.mark.parametrize("kwargs,match", [
        ({}, "at least one part"),
        ({"text": [""], "json": []}, None),  # an empty text part is still a part
        ({"json": ["{not json"]}, "valid JSON"),
        ({"text": [1]}, "strings"),
        ({"image": [b"raw"]}, "from_bytes"),
    ])
    def test_validation(self, kwargs, match):
        if match is None:
            assert DeploymentInvokeRequest(**kwargs).text == [""]
            return
        with pytest.raises(BadParameterError, match=match):
            DeploymentInvokeRequest(**kwargs)

    def test_a_list_is_several_json_parts(self):
        assert DeploymentInvokeRequest(json=[{"a": 1}, [1, 2]]).json == [{"a": 1}, [1, 2]]
        assert DeploymentInvokeRequest(json={"a": 1}).json == [{"a": 1}]
        files = DeploymentInvokeRequest(json=[[1, 2]]).multipart_files()
        assert [body for _, (_, body, _) in files] == [b"[1, 2]"]

    def test_file_needs_exactly_one_source_and_a_name(self, tmp_path):
        with pytest.raises(BadParameterError):
            DeploymentInvokeFile(filename="a.png")
        with pytest.raises(BadParameterError):
            DeploymentInvokeFile(filename="", data=b"x")
        with pytest.raises(BadParameterError, match="Not a file"):
            DeploymentInvokeFile.from_path(tmp_path / "missing.png")
        assert DeploymentInvokeFile.from_bytes(b"x", "blob").content_type == "application/octet-stream"

    def test_size_limit(self, monkeypatch):
        monkeypatch.setattr(invoke_module, "MAX_REQUEST_BYTES", 10)
        request = DeploymentInvokeRequest(file=DeploymentInvokeFile.from_bytes(b"x" * 11, "big.bin"))
        with pytest.raises(BadParameterError, match="1 GiB"):
            request.multipart_files()


class TestCall:
    def test_success(self):
        body = _multipart([
            ("video", "result.mp4", "video/mp4", VIDEO),
            ("json", None, "application/json", b'{"seed": 7, "model": "base"}'),
            ("text", None, "text/plain; charset=utf-8", "답".encode()),
        ], preamble=b"ignored preamble\r\n")

        result, post = _call(_response(200, body, f'multipart/form-data; boundary="{BOUNDARY}"'))

        post.assert_called_once()  # never retried
        args, kwargs = post.call_args
        assert args[0] == f"{HOST}/graphql/model-deployments/dataset%201/01JDEPLOY/invoke"
        assert kwargs["headers"] == {"Authorization": "Basic dGVzdC1rZXk6dGVzdC1zZWNyZXQ="}
        assert kwargs["allow_redirects"] is False
        assert kwargs["timeout"] == DEFAULT_INVOKE_TIMEOUT
        assert [name for name, _ in kwargs["files"]] == ["text"]

        assert [part.name for part in result] == ["video", "json", "text"]
        assert result.videos[0].data == VIDEO
        assert result.videos[0].filename == "result.mp4"
        assert result.videos[0].content_type == "video/mp4"
        assert result.json_values == [{"seed": 7, "model": "base"}]
        assert result.texts == ["답"]
        assert result.images == [] and result.files == []

    def test_save(self, tmp_path):
        body = _multipart([("video", "../../evil/result.mp4", "video/mp4", VIDEO)])
        result, _ = _call(_response(200, body, f"multipart/form-data; boundary={BOUNDARY}"))

        saved = result.videos[0].save(tmp_path)

        assert saved == str(tmp_path / "result.mp4")
        assert (tmp_path / "result.mp4").read_bytes() == VIDEO
        assert result.videos[0].save(tmp_path / "named.mp4") == str(tmp_path / "named.mp4")

    def test_timeout_argument(self):
        _, post = _call(_response(200, _multipart([("text", None, None, b"x")]),
                                  f"multipart/form-data; boundary={BOUNDARY}"), timeout=30)
        assert post.call_args[1]["timeout"] == 30

    @pytest.mark.parametrize("status,code,expected", [
        (400, "INVALID_INPUT", InvalidInputError),
        (403, "FORBIDDEN", ForbiddenError),
        (404, "NOT_FOUND", NotFoundError),
        (409, "NOT_READY", ConflictError),
        (413, "PAYLOAD_TOO_LARGE", InvalidInputError),
        (415, "UNSUPPORTED_MEDIA_TYPE", InvalidInputError),
        (422, "UNPROCESSABLE", InvalidInputError),
        (503, "BUSY", ConflictError),
        (503, "NOT_READY", ConflictError),
    ])
    def test_errors_with_a_general_meaning(self, status, code, expected):
        body = json.dumps({"error": {"code": code, "message": "shown to users"}}).encode()
        with pytest.raises(expected) as raised:
            _call(_response(status, body, "application/json", {"Retry-After": "5"}))
        error = raised.value
        assert isinstance(error, DeploymentInvokeError)
        assert isinstance(error, UnknownError) or isinstance(error, NotFoundError)
        assert (error.status_code, error.code, error.message, error.retry_after) == (status, code, "shown to users", "5")
        assert error.details == {"status": status, "retryAfter": "5"}

    @pytest.mark.parametrize("status,code", [
        (401, "UNAUTHENTICATED"), (502, "UPSTREAM_UNAVAILABLE"), (503, "ENDPOINT_TOKEN_UNAVAILABLE"),
        (504, "TIMEOUT"), (500, "INTERNAL_ERROR"),
    ])
    def test_other_errors(self, status, code):
        body = json.dumps({"error": {"code": code, "message": "m"}}).encode()
        with pytest.raises(DeploymentInvokeError) as raised:
            _call(_response(status, body, "application/json"))
        assert type(raised.value) is DeploymentInvokeError
        assert raised.value.code == code
        if status == 401:
            assert "system SDK" in str(raised.value)

    def test_error_without_the_contract_body(self):
        with pytest.raises(DeploymentInvokeError) as raised:
            _call(_response(413, b"<html>Payload Too Large</html>", "text/html"))
        assert raised.value.code is None
        assert raised.value.message == "HTTP 413"
        assert isinstance(raised.value, InvalidInputError)

    def test_redirect_is_not_followed(self):
        with pytest.raises(BadResponseError, match="redirect"):
            _call(_response(302, b"", headers={"Location": "https://elsewhere.example.test/"}))

    def test_connection_error(self):
        service = _service()
        with patch("spb_onprem.model_deployments.service.requests.post",
                   side_effect=requests.exceptions.ConnectionError("refused")) as post:
            with pytest.raises(BadResponseError, match="ConnectionError"):
                service.invoke_model_deployment("d", "x", DeploymentInvokeRequest(text="hi"))
        post.assert_called_once()

    @pytest.mark.parametrize("content_type,body,match", [
        ("application/json", b"{}", "multipart/form-data"),
        ("multipart/form-data", b"--b1f0--\r\n", "multipart/form-data"),  # no boundary
        (f"multipart/form-data; boundary={BOUNDARY}",
         f'--{BOUNDARY}\r\nContent-Disposition: form-data; name="video"\r\n\r\npartial'.encode(), "cut off"),
        (f"multipart/form-data; boundary={BOUNDARY}",
         f"--{BOUNDARY}\r\nContent-Type: text/plain\r\n\r\nx\r\n--{BOUNDARY}--".encode(), "without a name"),
    ])
    def test_bad_success_responses(self, content_type, body, match):
        with pytest.raises(BadResponseError, match=match):
            _call(_response(200, body, content_type))

    def test_request_type_is_checked(self):
        with pytest.raises(BadParameterError):
            _service().invoke_model_deployment("d", "x", {"text": ["hi"]})

    def test_system_sdk_sends_its_header_and_gets_a_clear_401(self):
        service = _service(system=True)
        body = json.dumps({"error": {"code": "UNAUTHENTICATED", "message": "Authentication is required."}})
        with patch("spb_onprem.model_deployments.service.requests.post",
                   return_value=_response(401, body.encode(), "application/json")) as post:
            with pytest.raises(DeploymentInvokeError, match="access key"):
                service.invoke_model_deployment("d", "x", DeploymentInvokeRequest(text="hi"))
        assert post.call_args[1]["headers"] == {"x-user-email": "system@example.test"}


def test_parse_rfc2231_filename_and_charset():
    body = (
        f"--{BOUNDARY}\r\n"
        "Content-Disposition: form-data; name=\"file\"; filename*=UTF-8''%EA%B2%B0%EA%B3%BC.txt\r\n"
        "Content-Type: text/plain; charset=euc-kr\r\n\r\n"
    ).encode() + "결과".encode("euc-kr") + f"\r\n--{BOUNDARY}--".encode()

    part = parse_multipart(f"multipart/form-data; boundary={BOUNDARY}", body)[0]

    assert part.filename == "결과.txt"
    assert part.text == "결과"
