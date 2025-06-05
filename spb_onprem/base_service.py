from typing import Optional, Dict, Any, ClassVar
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
            retry = RetryWithJitter(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
                allowed_methods=frozenset(allowed_methods),
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            BaseService._retry_session = session
        return BaseService._retry_session

    def request_gql(self, query: Any, variables: Dict[str, Any]):
        """Request Graphql query to the server."""
        payload = {
            "query": query["query"],
            "variables": variables
        }
        
        # Create a new session for each request
        session = self.requests_retry_session()
        
        try:
            response = session.post(
                self.endpoint,
                json=payload,
                headers=self._auth_user.auth_headers
            )
            response.raise_for_status()
            
            result = response.json()
            if not isinstance(result, dict):
                raise BadRequestError(f"Invalid response format: {type(result).__name__}, expected dict")

            # Check for GraphQL errors
            if 'errors' in result and result['errors']:
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
