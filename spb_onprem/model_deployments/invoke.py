"""Request and response of the invoke relay (endpoint server contract v1).

A deployment is called through app-api:
``POST {host}/graphql/model-deployments/{datasetId}/{deploymentId}/invoke``
with ``multipart/form-data``. Parts are named ``text``, ``json``, ``image``,
``video`` and ``file``; each name may repeat and keeps its order. A
successful response is ``multipart/form-data`` with the same part names; an
error is ``{"error": {"code", "message"}}``.
"""
import json as jsonlib
import mimetypes
import os
from dataclasses import dataclass, field
from email.message import Message
from typing import Any, Iterator, List, Optional, Sequence, Tuple, Union

from spb_onprem.exceptions import BadParameterError, BadResponseError

from .exceptions import (
    DeploymentInvokeConflictError,
    DeploymentInvokeError,
    DeploymentInvokeForbiddenError,
    DeploymentInvokeInvalidInputError,
    DeploymentInvokeNotFoundError,
)

PART_NAMES = ("text", "json", "image", "video", "file")
FILE_PART_NAMES = ("image", "video", "file")
#: The relay refuses a request larger than this (413).
MAX_REQUEST_BYTES = 1024 * 1024 * 1024

PathLike = Union[str, "os.PathLike[str]"]


@dataclass
class DeploymentInvokeFile:
    """A file part (``image``, ``video`` or ``file``).

    Build it with ``from_path`` or ``from_bytes``. ``filename`` matters: model
    servers read the file type from its extension. ``content_type`` is guessed
    from the file name when it is not given.
    """

    filename: str
    data: Optional[bytes] = None
    path: Optional[str] = None
    content_type: Optional[str] = None

    def __post_init__(self):
        if (self.data is None) == (self.path is None):
            raise BadParameterError("A DeploymentInvokeFile needs exactly one of data or path.")
        if not isinstance(self.filename, str) or not self.filename.strip():
            raise BadParameterError("A DeploymentInvokeFile needs a filename.")
        if self.data is not None and not isinstance(self.data, (bytes, bytearray)):
            raise BadParameterError("DeploymentInvokeFile.data must be bytes.")
        if self.content_type is None:
            self.content_type = mimetypes.guess_type(self.filename)[0] or "application/octet-stream"

    @classmethod
    def from_path(cls, path: PathLike, content_type: Optional[str] = None,
                  filename: Optional[str] = None) -> "DeploymentInvokeFile":
        """A file read from ``path`` when the request is sent."""
        path = os.fspath(path)
        if not os.path.isfile(path):
            raise BadParameterError(f"Not a file: {path}")
        return cls(filename=filename or os.path.basename(path), path=path, content_type=content_type)

    @classmethod
    def from_bytes(cls, data: bytes, filename: str,
                   content_type: Optional[str] = None) -> "DeploymentInvokeFile":
        """A file in memory. ``filename`` is required (for example ``input.png``)."""
        return cls(filename=filename, data=bytes(data), content_type=content_type)

    def size(self) -> int:
        return len(self.data) if self.data is not None else os.path.getsize(self.path)

    def read(self) -> bytes:
        if self.data is not None:
            return bytes(self.data)
        with open(self.path, "rb") as source:
            return source.read()


def _as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _as_file(value: Any, name: str) -> DeploymentInvokeFile:
    if isinstance(value, DeploymentInvokeFile):
        return value
    if isinstance(value, (str, os.PathLike)):
        return DeploymentInvokeFile.from_path(value)
    raise BadParameterError(
        f"{name} parts must be DeploymentInvokeFile or file paths; "
        "use DeploymentInvokeFile.from_bytes(data, filename) for bytes."
    )


@dataclass
class DeploymentInvokeRequest:
    """What to send to a deployment. Each argument takes one value or a list.

    Args:
        text: Text parts (for example a prompt or a question).
        json: JSON parts, one JSON document each (model options such as a
            seed). A dict, number or bool is serialized; a str is sent as it is
            and must already be valid JSON. A list means several parts, so
            send a JSON array as ``[[...]]`` or as a str.
        image / video / file: File parts: ``DeploymentInvokeFile`` or a path.

    Which parts a model reads is up to its server (see the template's
    documentation). At least one part is required.
    """

    text: List[str] = field(default_factory=list)
    json: List[Any] = field(default_factory=list)
    image: List[DeploymentInvokeFile] = field(default_factory=list)
    video: List[DeploymentInvokeFile] = field(default_factory=list)
    file: List[DeploymentInvokeFile] = field(default_factory=list)

    def __post_init__(self):
        self.text = _as_list(self.text)
        for value in self.text:
            if not isinstance(value, str):
                raise BadParameterError("text parts must be strings.")
        self.json = _as_list(self.json)
        for value in self.json:
            if isinstance(value, str):
                try:
                    jsonlib.loads(value)
                except ValueError as error:
                    raise BadParameterError(f"A json part given as str must be valid JSON ({error}).") from None
            else:
                try:
                    jsonlib.dumps(value, allow_nan=False)
                except (TypeError, ValueError) as error:
                    raise BadParameterError(f"A json part must be JSON serializable ({error}).") from None
        for name in FILE_PART_NAMES:
            setattr(self, name, [_as_file(item, name) for item in _as_list(getattr(self, name))])
        if not any(getattr(self, name) for name in PART_NAMES):
            raise BadParameterError("An invoke request needs at least one part.")

    def multipart_files(self) -> List[Tuple[str, Tuple[Optional[str], bytes, str]]]:
        """The parts in contract order, as the ``files`` argument of ``requests``."""
        parts = []
        for value in self.text:
            parts.append(("text", (None, value.encode("utf-8"), "text/plain; charset=utf-8")))
        for value in self.json:
            text = value if isinstance(value, str) else jsonlib.dumps(value, ensure_ascii=False, allow_nan=False)
            parts.append(("json", (None, text.encode("utf-8"), "application/json")))
        total = sum(len(body) for _, (_, body, _) in parts)
        for name in FILE_PART_NAMES:
            for item in getattr(self, name):
                total += item.size()
                if total > MAX_REQUEST_BYTES:
                    raise BadParameterError("An invoke request can be at most 1 GiB.")
                parts.append((name, (item.filename, item.read(), item.content_type)))
        return parts


@dataclass(frozen=True)
class DeploymentInvokePart:
    """One part of a response."""

    name: str
    data: bytes
    filename: Optional[str] = None
    content_type: Optional[str] = None

    @property
    def text(self) -> str:
        """The part as text (UTF-8 unless the part says otherwise)."""
        charset = "utf-8"
        if self.content_type:
            message = Message()
            message["content-type"] = self.content_type
            charset = message.get_content_charset() or "utf-8"
        return self.data.decode(charset, errors="replace")

    def json(self) -> Any:
        """The part parsed as JSON."""
        return jsonlib.loads(self.text)

    def save(self, path: PathLike) -> str:
        """Write the bytes to ``path``. If ``path`` is a directory, the part's file name is used."""
        path = os.fspath(path)
        if os.path.isdir(path):
            # Only the base name: a file name from a server never picks the directory.
            name = os.path.basename((self.filename or "").replace("\\", "/")) or self.name
            if name in (".", ".."):
                name = self.name
            path = os.path.join(path, name)
        with open(path, "wb") as target:
            target.write(self.data)
        return path


@dataclass(frozen=True)
class DeploymentInvokeResult:
    """A successful response: its parts in order."""

    status_code: int
    content_type: str
    parts: Tuple[DeploymentInvokePart, ...]

    def get(self, name: str) -> List[DeploymentInvokePart]:
        """The parts with this name, in order."""
        return [part for part in self.parts if part.name == name]

    @property
    def texts(self) -> List[str]:
        return [part.text for part in self.get("text")]

    @property
    def json_values(self) -> List[Any]:
        """Every ``json`` part, parsed."""
        return [part.json() for part in self.get("json")]

    @property
    def images(self) -> List[DeploymentInvokePart]:
        return self.get("image")

    @property
    def videos(self) -> List[DeploymentInvokePart]:
        return self.get("video")

    @property
    def files(self) -> List[DeploymentInvokePart]:
        return self.get("file")

    def __iter__(self) -> Iterator[DeploymentInvokePart]:
        return iter(self.parts)


def _header_message(headers: Sequence[Tuple[str, str]]) -> Message:
    message = Message()
    for name, value in headers:
        message[name] = value
    return message


def parse_multipart(content_type: str, body: bytes) -> List[DeploymentInvokePart]:
    """Split a ``multipart/form-data`` body into parts.

    Raises:
        BadResponseError: If the body is not multipart or is cut off.
    """
    header = _header_message([("content-type", content_type or "")])
    boundary = header.get_param("boundary")
    if header.get_content_type() != "multipart/form-data" or not boundary:
        raise BadResponseError(f"Expected a multipart/form-data response, got {content_type!r}.")
    boundary = boundary.encode("latin-1")
    delimiter = b"\r\n--" + boundary
    # The first delimiter may start the body without a CRLF in front.
    segments = (b"\r\n" + body).split(delimiter)
    parts: List[DeploymentInvokePart] = []
    closed = False
    for segment in segments[1:]:
        if segment.startswith(b"--"):
            closed = True
            break
        line_end = segment.find(b"\r\n")
        if line_end < 0 or segment[:line_end].strip(b" \t"):
            raise BadResponseError("Malformed multipart response (delimiter line).")
        head_end = segment.find(b"\r\n\r\n", line_end)
        if head_end < 0:
            raise BadResponseError("Malformed multipart response (part headers).")
        raw_headers = segment[line_end + 2:head_end].decode("utf-8", errors="replace")
        headers = []
        for line in raw_headers.split("\r\n"):
            if not line.strip():
                continue
            name, sep, value = line.partition(":")
            if not sep:
                raise BadResponseError("Malformed multipart response (part header line).")
            headers.append((name.strip(), value.strip()))
        message = _header_message(headers)
        name = message.get_param("name", header="content-disposition")
        if not name:
            raise BadResponseError("Malformed multipart response (part without a name).")
        parts.append(DeploymentInvokePart(
            name=str(name),
            data=segment[head_end + 4:],
            filename=message.get_filename(),
            content_type=message.get("content-type"),
        ))
    if not closed:
        raise BadResponseError("The multipart response ended before its closing delimiter (cut off?).")
    return parts


#: General SDK error class per HTTP status; the body's code decides for 503.
_ERROR_CLASSES = {
    400: DeploymentInvokeInvalidInputError,
    403: DeploymentInvokeForbiddenError,
    404: DeploymentInvokeNotFoundError,
    409: DeploymentInvokeConflictError,
    413: DeploymentInvokeInvalidInputError,
    415: DeploymentInvokeInvalidInputError,
    422: DeploymentInvokeInvalidInputError,
}
_BUSY_CODES = {"BUSY", "NOT_READY"}


def invoke_error(status_code: int, body: bytes, retry_after: Optional[str] = None) -> DeploymentInvokeError:
    """The error for a non-2xx response with the contract body ``{"error": {"code", "message"}}``."""
    code: Optional[str] = None
    message = f"HTTP {status_code}"
    try:
        error = jsonlib.loads(body.decode("utf-8")).get("error")
        if isinstance(error, dict):
            if isinstance(error.get("code"), str):
                code = error["code"]
            if isinstance(error.get("message"), str):
                message = error["message"]
    except (ValueError, AttributeError, UnicodeDecodeError):
        pass
    if status_code == 401 and code == "UNAUTHENTICATED":
        message += (" The invoke relay accepts an access key (Basic) or a user token;"
                    " the system SDK (no config file) cannot call it.")
    cls = _ERROR_CLASSES.get(status_code, DeploymentInvokeError)
    if status_code == 503 and code in _BUSY_CODES:
        cls = DeploymentInvokeConflictError
    return cls(message, status_code=status_code, code=code, retry_after=retry_after)
