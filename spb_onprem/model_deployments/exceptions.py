"""Errors of ``ModelDeploymentService.invoke_model_deployment``.

Every invoke error is a ``DeploymentInvokeError``. Those that have a general
meaning are also the general SDK error, so ``except ForbiddenError`` (and the
others) catches them as for any other call:

- 403 FORBIDDEN: ``ForbiddenError``
- 404 NOT_FOUND: ``NotFoundError``
- 409 NOT_READY, 503 BUSY / NOT_READY: ``ConflictError`` (the deployment is
  not ready or busy; ``retry_after`` has the server's hint in seconds, if any)
- 400 INVALID_INPUT, 413, 415, 422 UNPROCESSABLE: ``InvalidInputError``

Others (401 UNAUTHENTICATED, 502, 504 TIMEOUT, 500, ...) are plain
``DeploymentInvokeError``.
"""
from typing import Optional

from spb_onprem.exceptions import (
    ConflictError,
    ForbiddenError,
    GraphQLError,
    InvalidInputError,
    NotFoundError,
)


class DeploymentInvokeError(GraphQLError):
    """The invoke relay or the model server refused or failed a call.

    Attributes:
        status_code (int): The HTTP status.
        code (Optional[str]): ``error.code`` of the response body, for example
            ``NOT_READY``, ``TIMEOUT`` or ``INVALID_INPUT``.
        message (str): ``error.message`` of the response body (safe to show).
        retry_after (Optional[str]): The ``Retry-After`` header, if any.
        details (dict): ``{"status": ..., "retryAfter": ...}``.
    """

    def __init__(self, message: str, status_code: int, code: Optional[str] = None,
                 retry_after: Optional[str] = None):
        super().__init__(
            f"Model deployment invoke failed (HTTP {status_code}"
            + (f", {code}" if code else "") + f"): {message}",
            code=code,
            details={"status": status_code, "retryAfter": retry_after},
        )
        self.status_code = status_code
        self.message = message
        self.retry_after = retry_after


class DeploymentInvokeForbiddenError(DeploymentInvokeError, ForbiddenError):
    """403: the caller has no role in the dataset that allows invoking."""


class DeploymentInvokeNotFoundError(DeploymentInvokeError, NotFoundError):
    """404: the dataset or deployment does not exist."""


class DeploymentInvokeConflictError(DeploymentInvokeError, ConflictError):
    """The deployment is not READY (409), or the server is loading or busy (503)."""


class DeploymentInvokeInvalidInputError(DeploymentInvokeError, InvalidInputError):
    """The request was refused: invalid or missing parts, too large, or not processable."""
