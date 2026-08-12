import pytest
from unittest.mock import Mock, patch

import requests

from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import (
    BadRequestParameterError,
    BadRequestError,
    RequestError,
)


class TestBaseServiceRequestErrorHandling:
    """Exception translation in BaseService.request().

    request() is inherited by the contents, diagnoses, models, inferences and
    reports services, so the exceptions it surfaces are part of their contract.
    """

    def setup_method(self):
        self.service = BaseService()

    @staticmethod
    def _session_raising(exc):
        session = Mock()
        session.request.side_effect = exc
        return session

    def test_value_error_raises_bad_request_parameter_error(self):
        """A ValueError from the underlying request surfaces as BadRequestParameterError."""
        session = self._session_raising(ValueError("bad value"))
        with patch.object(BaseService, "requests_retry_session", return_value=session):
            with pytest.raises(BadRequestParameterError):
                self.service.request("GET", "http://example.com", headers={})

    def test_value_error_preserves_original_cause(self):
        """The BadRequestParameterError chains the original ValueError via `from e`."""
        original = ValueError("bad value")
        session = self._session_raising(original)
        with patch.object(BaseService, "requests_retry_session", return_value=session):
            with pytest.raises(BadRequestParameterError) as excinfo:
                self.service.request("GET", "http://example.com", headers={})
        assert excinfo.value.__cause__ is original

    def test_request_exception_raises_bad_request_error(self):
        """A requests RequestException still surfaces as BadRequestError."""
        session = self._session_raising(requests.exceptions.ConnectionError("boom"))
        with patch.object(BaseService, "requests_retry_session", return_value=session):
            with pytest.raises(BadRequestError):
                self.service.request("GET", "http://example.com", headers={})

    def test_unexpected_exception_raises_request_error(self):
        """Any other exception still surfaces as RequestError."""
        session = self._session_raising(RuntimeError("boom"))
        with patch.object(BaseService, "requests_retry_session", return_value=session):
            with pytest.raises(RequestError):
                self.service.request("GET", "http://example.com", headers={})
