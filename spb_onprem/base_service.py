from typing import Optional, Dict, Any, ClassVar
import json
import os
import random

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from spb_onprem.users.entities import AuthUser
from spb_onprem.exceptions import (
    NotFoundError,
    UnknownError,
    BadResponseError,
    BadRequestError,
    BaseSDKError,
    BadRequestParameterError,
    RequestError,
    ResponseError,
)

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
            session = session or requests.Session()
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
            text = _safe_dump(obj)
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
            response = session.post(
                self.endpoint,
                json=payload,
                headers=self._auth_user.auth_headers
            )
            _print_debug(
                "response_http",
                {
                    "status_code": response.status_code,
                    "elapsed_ms": int(response.elapsed.total_seconds() * 1000) if getattr(response, "elapsed", None) else None,
                },
            )
            response.raise_for_status()
            
            result = response.json()
            _print_debug("response_json", result)
            if not isinstance(result, dict):
                raise BadRequestError(f"Invalid response format: {type(result).__name__}, expected dict")

            # Check for GraphQL errors
            if 'errors' in result and result['errors']:
                _print_debug("response_graphql_errors", result.get("errors"))
                for error in result['errors']:
                    if error['code'] == 'NOT_FOUND':
                        raise NotFoundError(error['message'])
                error_messages = [error.get('message', 'Unknown error') for error in result['errors']]
                raise UnknownError(f"GraphQL errors: {', '.join(error_messages)}")
            
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
                response_text = e.response.text[:1000] if e.response.text else "No response body"
                print(f"GraphQL Request Failed - {error_details}: {response_text}")
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"GraphQL Request Failed - {error_details}")
                logger.error(f"Response body: {response_text}")
                logger.error(f"Request URL: {e.response.url}")
                logger.error(f"Request headers: {dict(e.response.request.headers) if e.response.request else 'N/A'}")
            raise BadResponseError(f"HTTP request failed: {str(e)}") from e
        except BaseSDKError as e:
            raise e
        except Exception as e:
            raise ResponseError(f"Unexpected error: {str(e)}") from e
        finally:
            # Close the session after use
            session.close()

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        json_data: Optional[dict] = None,
        timeout: int = 30
    ):
        session = self.requests_retry_session()
        try:
            response = session.request(
                method=method.upper(),
                url=url,
                headers={
                    **headers,
                    **self._auth_user.auth_headers
                },
                params=params,
                data=data,
                json=json_data,
                timeout=timeout
            )
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the HTTP request: {str(e)}")
            raise BadRequestError(f"HTTP request failed: {str(e)}") from e
        except ValueError:
            raise BadRequestParameterError("Failed to parse the HTTP response as JSON.") from e
        except Exception as e:
            raise RequestError(f"An error occurred while processing the HTTP response: {str(e)}") from e
        finally:
            session.close()
