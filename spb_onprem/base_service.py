from typing import Optional, Dict, Any, ClassVar
from urllib.parse import urljoin, urlsplit, urlunsplit
import json
import logging
import os
import random
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry, parse_url

from spb_onprem.users.entities import AuthUser
from spb_onprem.exceptions import (
    ConflictError,
    ForbiddenError,
    GraphQLError,
    InvalidInputError,
    NotFoundError,
    BadResponseError,
    BadRequestError,
    BaseSDKError,
    BadRequestParameterError,
    RequestError,
    ResponseError,
)

_URL_QUERY = re.compile(r"(https?://[^\s?#'\"]+)\?[^\s#'\"]*")
# A query-like part in any form, also a relative one such as urllib3's
# "Max retries exceeded with url: /bucket/key?X-Amz-Signature=...".
_ANY_QUERY = re.compile(r"\?[^\s#'\"<>]*=[^\s#'\"<>]*")

#: Request headers never written to logs (lower case).
SENSITIVE_HEADERS = frozenset({"authorization", "proxy-authorization", "cookie", "x-api-key", "x-user-email"})


def redact_url_queries(text: str, *urls: Optional[str]) -> str:
    """Hide URL query strings, such as the signature of a presigned storage URL.

    The query of each given URL is replaced wherever it appears, whatever the
    form of the message (absolute URL, relative path, encoded). Then any
    remaining ``?key=value`` part is hidden too.
    """
    text = str(text)
    for url in urls:
        if not url:
            continue
        for candidate in {url, _prepared_url(url)}:
            if not candidate:
                continue
            try:
                query = urlsplit(candidate).query
            except ValueError:
                query = candidate.partition("?")[2]
            if query:
                text = text.replace(query, "<redacted>")
    text = _URL_QUERY.sub(r"\1?<redacted>", text)
    return _ANY_QUERY.sub("?<redacted>", text)


def _prepared_url(url: str) -> Optional[str]:
    """The URL as requests sends it, or None if requests cannot parse it."""
    try:
        prepared = requests.models.PreparedRequest()
        prepared.prepare_url(url, None)
        return prepared.url
    except Exception:  # noqa: BLE001 - only used to find text to hide
        return None


def redact_headers(headers) -> Dict[str, Any]:
    return {k: ("<redacted>" if str(k).lower() in SENSITIVE_HEADERS else v) for k, v in dict(headers).items()}


#: Where the platform host is set, for error messages.
HOST_SETTING = "host in ~/.spb/onprem-config, or SUNRISE_SERVER_URL / SUPERB_SYSTEM_SDK_HOST for the system SDK"


def _shown_url(url: str) -> str:
    """The URL for a message: no user:password@, query or fragment."""
    parts = urlsplit(url)
    return urlunsplit((
        parts.scheme,
        parts.netloc.rpartition("@")[2],
        parts.path,
        "<redacted>" if parts.query else "",
        "",
    ))


def redirect_error(request_url: str, response) -> BadResponseError:
    """The error for a platform API request that got a redirect (3xx).

    The SDK sends platform API requests without following redirects: a POST
    redirected with 301/302/303 is resent as GET without its body (the server
    then answers with an unclear error such as an Apollo CSRF 400), and
    following would send the credentials to another URL. Nothing is resent.
    """
    location = (getattr(response, "headers", None) or {}).get("Location")
    try:
        target = urljoin(request_url, location) if location else None
        shown = _shown_url(target) if target else None
        to_https = bool(target) and (
            urlsplit(request_url).scheme.lower() == "http" and urlsplit(target).scheme.lower() == "https"
        )
    except ValueError:  # a malformed Location
        shown, to_https = None, False
    message = f"The platform answered with a redirect (HTTP {response.status_code}"
    if shown:
        message += f" to {shown}"
    message += (
        "). The SDK does not follow redirects for platform API requests: a redirected POST can be "
        "resent as GET without its body (HTTP 301/302/303) and fail with an unclear error such as an "
        "Apollo CSRF HTTP 400, and the credentials would go to another URL."
    )
    if to_https:
        message += f" The host uses http:// but the server wants https://. Set the host to https:// ({HOST_SETTING})."
    else:
        message += f" Check the platform host ({HOST_SETTING})."
    return BadResponseError(message)


def post_without_redirects(post, url: str, **kwargs):
    """``post(url, **kwargs)`` (a session's or requests' post) without following redirects.

    requests still prepares the next request of a redirect it does not follow,
    so a malformed Location fails inside ``post`` (e.g. ValueError "Invalid
    IPv6 URL"). If the response hook saw a redirect, that raises
    ``redirect_error`` instead. The caller checks the returned status.
    """
    redirects = []

    def keep_redirect(response, *args, **hook_kwargs):
        if 300 <= response.status_code < 400:
            redirects.append(response)

    try:
        return post(url, allow_redirects=False, hooks={"response": keep_redirect}, **kwargs)
    except Exception:
        if redirects:
            raise redirect_error(url, redirects[-1]) from None
        raise


class _RedactUrlQueryFilter(logging.Filter):
    """Hides URL query strings (presigned signatures) in urllib3 log records.

    urllib3 logs the request path with its query, also at WARNING when it
    retries ("Retrying (...) after connection broken by '...':
    /bucket/key?X-Amz-Signature=..."). Only the query part is replaced; the
    rest of the record is unchanged.
    """

    #: Marks the filter, so it is added once even if this module is loaded again.
    spb_redact_url_query = True

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 - never break logging
            return True
        if "?" in message:
            redacted = redact_url_queries(message)
            if redacted != message:
                record.msg = redacted
                record.args = ()
        return True


#: urllib3 loggers that write request URLs: the connection pool (WARNING on
#: retries, DEBUG per request) and the retry counter (DEBUG).
URLLIB3_URL_LOGGERS = ("urllib3.connectionpool", "urllib3.util.retry")


def install_urllib3_log_redaction() -> None:
    """Add the query-hiding filter to the urllib3 loggers once (done on import)."""
    for name in URLLIB3_URL_LOGGERS:
        logger = logging.getLogger(name)
        if not any(getattr(item, "spb_redact_url_query", False) for item in logger.filters):
            logger.addFilter(_RedactUrlQueryFilter())


install_urllib3_log_redaction()


class _PlatformSession(requests.Session):
    """A session that drops the system user header when a redirect leaves the host.

    requests already drops ``Authorization`` then (``should_strip_auth``); the
    system SDK sends ``x-user-email`` instead, which requests would forward.
    """

    def rebuild_auth(self, prepared_request, response):
        if "x-user-email" in prepared_request.headers and self.should_strip_auth(
            response.request.url, prepared_request.url
        ):
            del prepared_request.headers["x-user-email"]
        super().rebuild_auth(prepared_request, response)


#: SDK exception per platform error code. Other codes raise GraphQLError (an UnknownError).
GRAPHQL_ERROR_CLASSES = {
    'BAD_REQUEST': InvalidInputError,
    'FORBIDDEN': ForbiddenError,
    'CONFLICT': ConflictError,
}


class RetryWithJitter(Retry):
    def get_backoff_time(self):
        base_backoff = super().get_backoff_time()
        jitter = base_backoff * random.uniform(0.5, 1.5)
        return jitter


class BaseService():
    """The BaseService class is an abstract base class that defines the interface for services that handle data operations.
    """
    _retry_session: ClassVar[Optional[requests.Session]] = None
    _auth_user: Optional[AuthUser] = None
    
    def __init__(self):
        self._auth_user = AuthUser.get_instance()
        if self._auth_user.is_system_sdk:
            self.endpoint = f"{self._auth_user.host}/system/graphql/"
        else:
            self.endpoint = f"{self._auth_user.host}/graphql/"
    
    @classmethod
    def requests_retry_session(
        cls,
        retries=5,
        backoff_factor=2,
        status_forcelist=(500, 502, 504),
        session=None,
        allowed_methods=[
            'GET',
            'POST',
            'PUT',
            'DELETE',
            'OPTIONS',
            'HEAD',
            'PATCH',
            'TRACE',
            'CONNECT'
        ]
    ) -> requests.Session:
        if BaseService._retry_session is None:
            session = session or _PlatformSession()
            # urllib3 < 1.26에서는 method_whitelist, >= 1.26에서는 allowed_methods 사용
            try:
                retry = RetryWithJitter(
                    total=retries,
                    read=retries,
                    connect=retries,
                    backoff_factor=backoff_factor,
                    status_forcelist=status_forcelist,
                    allowed_methods=frozenset(allowed_methods),
                )
            except TypeError:
                # Fallback for older urllib3 versions
                retry = RetryWithJitter(
                    total=retries,
                    read=retries,
                    connect=retries,
                    backoff_factor=backoff_factor,
                    status_forcelist=status_forcelist,
                    method_whitelist=frozenset(allowed_methods),
                )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            BaseService._retry_session = session
        return BaseService._retry_session

    @staticmethod
    def _graphql_error_code(error: Dict[str, Any]) -> Optional[str]:
        """The error code: top-level ``code`` first, then ``extensions.code``."""
        code = error.get('code')
        if code:
            return code
        extensions = error.get('extensions')
        if isinstance(extensions, dict):
            return extensions.get('code')
        return None

    @staticmethod
    def _graphql_error_details(error: Dict[str, Any]) -> Dict[str, Any]:
        """The error details: top-level ``details`` first, then ``extensions.details``."""
        details = error.get('details')
        if not isinstance(details, dict):
            extensions = error.get('extensions')
            details = extensions.get('details') if isinstance(extensions, dict) else None
        return details if isinstance(details, dict) else {}

    @classmethod
    def _graphql_error_message(cls, error: Dict[str, Any]) -> str:
        message = error.get('message', 'Unknown error')
        code = cls._graphql_error_code(error)
        return f"[{code}] {message}" if code else message

    def request_gql(self, query: Any, variables: Dict[str, Any]):
        """Request Graphql query to the server."""
        debug_gql = os.environ.get("SDK_DEBUG_GQL") == "1"
        debug_max_chars_raw = os.environ.get("SDK_DEBUG_GQL_MAX_CHARS", "10000")
        try:
            debug_max_chars = int(debug_max_chars_raw)
        except ValueError:
            debug_max_chars = 10000

        def _safe_dump(obj: Any) -> str:
            try:
                return json.dumps(obj, ensure_ascii=False, default=str)
            except Exception:
                return str(obj)

        def _print_debug(title: str, obj: Any = None):
            if not debug_gql:
                return
            print(f"\n=== SDK_DEBUG_GQL: {title} ===")
            if obj is None:
                return
            # A response can hold presigned URLs (uploadURL); their query is a credential.
            text = redact_url_queries(_safe_dump(obj))
            if debug_max_chars > 0 and len(text) > debug_max_chars:
                text = text[:debug_max_chars] + "...<truncated>"
            print(text)

        payload = {
            "query": query["query"],
            "variables": variables
        }
        
        # Create a new session for each request
        session = self.requests_retry_session()
        
        try:
            _print_debug(
                "request",
                {
                    "endpoint": self.endpoint,
                    "operation": query.get("name"),
                    "variables": variables,
                },
            )
            # No redirects: see redirect_error. The credentials go to self.endpoint only.
            response = post_without_redirects(
                session.post,
                self.endpoint,
                json=payload,
                headers=self._auth_user.auth_headers,
            )
            _print_debug(
                "response_http",
                {
                    "status_code": response.status_code,
                    "elapsed_ms": int(response.elapsed.total_seconds() * 1000) if getattr(response, "elapsed", None) else None,
                },
            )
            if 300 <= response.status_code < 400:
                raise redirect_error(self.endpoint, response)
            response.raise_for_status()
            
            result = response.json()
            _print_debug("response_json", result)
            if not isinstance(result, dict):
                raise BadRequestError(f"Invalid response format: {type(result).__name__}, expected dict")

            # Check for GraphQL errors
            if 'errors' in result and result['errors']:
                _print_debug("response_graphql_errors", result.get("errors"))
                errors = [
                    error if isinstance(error, dict) else {"message": str(error)}
                    for error in result['errors']
                ]
                for error in errors:
                    if self._graphql_error_code(error) == 'NOT_FOUND':
                        not_found = NotFoundError(error.get('message', 'Not found'))
                        # e.g. details.resource tells a missing dataset, slice or VLM settings apart.
                        not_found.code = 'NOT_FOUND'
                        not_found.details = self._graphql_error_details(error)
                        raise not_found
                error_messages = [
                    self._graphql_error_message(error) for error in errors
                ]
                first = errors[0]
                code = self._graphql_error_code(first)
                error_class = GRAPHQL_ERROR_CLASSES.get(code, GraphQLError)
                raise error_class(
                    f"GraphQL errors: {', '.join(error_messages)}",
                    code=code,
                    details=self._graphql_error_details(first),
                    errors=errors,
                )
            
            # Validate response structure
            if 'data' not in result:
                raise BadResponseError("Missing 'data' field in response")
            
            query_name = query.get("name")
            if not query_name:
                raise BadResponseError("Missing query name in query object")
            
            # Handle different response structures
            data = result['data']
            
            # For other queries, expect the query name to be directly in data
            if query_name not in data:
                raise BadResponseError(f"Missing '{query_name}' in response data")
            
            return data[query_name]
            
        except requests.exceptions.RequestException as e:
            # Log detailed error information for debugging
            if hasattr(e, 'response') and e.response is not None:
                error_details = f"HTTP {e.response.status_code} Error"
                # The body can echo a URL (e.g. a presigned uploadURL); hide its query.
                response_text = (
                    redact_url_queries(e.response.text[:1000], self.endpoint)
                    if e.response.text else "No response body"
                )
                print(f"GraphQL Request Failed - {error_details}: {response_text}")
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"GraphQL Request Failed - {error_details}")
                logger.error(f"Response body: {response_text}")
                logger.error(f"Request URL: {e.response.url}")
                # Never log credentials: redact Authorization and other sensitive headers.
                if e.response.request is not None:
                    redacted = redact_headers(e.response.request.headers)
                else:
                    redacted = "N/A"
                logger.error(f"Request headers: {redacted}")
            # No exception chain: the cause's traceback could show what the message hides.
            raise BadResponseError(f"HTTP request failed: {redact_url_queries(str(e), self.endpoint)}") from None
        except BaseSDKError as e:
            raise e
        except Exception as e:
            raise ResponseError(f"Unexpected error: {str(e)}") from e
        finally:
            # Close the session after use
            session.close()

    @staticmethod
    def _origin(url: str):
        """(scheme, host, port) that requests actually connects to, default port filled in.

        Parsed the way requests does (PreparedRequest + urllib3), not with
        urlsplit, which reads some URLs differently (``http://a:1\\@b:2/``).

        Raises:
            BadRequestParameterError: If the URL has a backslash or a control
                character, or requests cannot parse it.
        """
        if not isinstance(url, str) or "\\" in url or any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in url):
            raise BadRequestParameterError("Invalid URL: it must not contain a backslash or a control character.")
        prepared = _prepared_url(url)
        if prepared is None:
            raise BadRequestParameterError(f"Invalid URL: {redact_url_queries(url, url)}")
        try:
            parts = parse_url(prepared)
        except Exception:  # noqa: BLE001 - urllib3 LocationParseError and the like
            raise BadRequestParameterError(f"Invalid URL: {redact_url_queries(url, url)}") from None
        scheme = (parts.scheme or "").lower()
        port = parts.port or {"http": 80, "https": 443}.get(scheme)
        return scheme, (parts.host or "").lower(), port

    def is_platform_url(self, url: str) -> bool:
        """True when ``url`` is on the platform API host (same scheme, host and port).

        Raises:
            BadRequestParameterError: If the URL is not valid (see ``_origin``).
        """
        return self._origin(url) == self._origin(self._auth_user.host)

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        json_data: Optional[dict] = None,
        timeout: int = 30,
        auth: Optional[bool] = None,
    ):
        """Send an HTTP request.

        The platform credentials (``Authorization`` or the system user header)
        are added only for the platform API host. A presigned storage URL
        (upload or download) carries its own signature, so it gets no
        platform credentials: they must not reach the storage host, and a
        strict S3 refuses a request with a second authorization.

        Args:
            auth (Optional[bool]): None (default) adds the credentials only when
                ``url`` is on the platform host. False never adds them (presigned
                URLs). True always adds them.
        """
        session = self.requests_retry_session()
        try:
            merged_headers = dict(headers or {})
            if auth is True or (auth is None and self.is_platform_url(url)):
                merged_headers.update(self._auth_user.auth_headers)
            response = session.request(
                method=method.upper(),
                url=url,
                headers=merged_headers,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout
            )
            response.raise_for_status()
            return response

        except BaseSDKError:
            raise
        except requests.exceptions.RequestException as e:
            # The message can hold the URL; a presigned URL's query is a credential.
            # No exception chain: the cause's traceback would show the whole URL.
            message = redact_url_queries(str(e), url)
            print(f"An error occurred during the HTTP request: {message}")
            raise BadRequestError(f"HTTP request failed: {message}") from None
        except ValueError as e:
            raise BadRequestParameterError(
                f"Invalid request or response: {redact_url_queries(str(e), url)}"
            ) from None
        except Exception as e:
            raise RequestError(
                f"An error occurred while processing the HTTP response: {redact_url_queries(str(e), url)}"
            ) from None
        finally:
            session.close()
