import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any, List, Mapping, Optional, Union

from spb_onprem.activities.deletion import require_id
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

from .filters import ModelDeploymentFilter, ModelDeploymentOrderBy, filter_variable

#: An absolute time, or how long from now.
ExpiresAt = Union[datetime, timedelta, str]

#: An ISO 8601 date and time that ends with a UTC offset or Z, basic or extended format:
#: 2026-10-20T09:00:00Z, 2026-10-20T09:00:00.5Z, ...+09:00, ...+0900, ...+09, 20261020T090000Z.
#: Only the offset is the point; the platform parses the rest.
_ISO_WITH_OFFSET = re.compile(
    r"\d{4}-?\d{2}-?\d{2}[Tt ]\d{2}(?::?\d{2}(?::?\d{2}(?:[.,]\d+)?)?)?"
    r"(?:[Zz]|[+-]\d{2}(?::?\d{2})?)"
)

#: The platform returns at most this many deployments per page.
MAX_PAGE_LENGTH = 100


def datetime_variable(value: Optional[ExpiresAt], name: str) -> Optional[str]:
    """An ISO 8601 UTC time for a GraphQL DateTime.

    A ``timedelta`` is counted from now. A naive ``datetime`` is local time.
    A ``str`` must be ISO 8601 with a UTC offset or ``Z``; it is sent as it is.
    One without an offset is refused (the platform would read it in its own
    time zone).
    """
    if value is None:
        return None
    if isinstance(value, timedelta):
        if value <= timedelta(0):
            raise BadParameterError(f"{name} must be in the future.")
        value = datetime.now(timezone.utc) + value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, str) and value.strip():
        # Python 3.8-3.10 fromisoformat is too narrow (".5Z", "+0900", basic format),
        # so only the presence of an offset is checked here.
        if not _ISO_WITH_OFFSET.fullmatch(value):  # no surrounding spaces or newlines either
            raise BadParameterError(
                f"{name} must be an ISO 8601 time with a UTC offset or Z (got {value!r}); "
                "e.g. 2026-10-20T09:00:00Z."
            )
        return value
    raise BadParameterError(f"{name} must be a datetime, a timedelta or an ISO 8601 string.")


def expiry_variable(
    expires_at: Optional[ExpiresAt],
    never_expires: bool,
    operation: str,
    note: str = "",
) -> dict:
    """A ``ModelDeploymentExpiryInput``: exactly one of ``expires_at`` or ``never_expires=True``.

    "Never expires" is a choice too, so neither is refused. ``expires_at``
    follows ``datetime_variable``; a passed time is refused by the platform.
    """
    if not isinstance(never_expires, bool):
        raise BadParameterError("never_expires must be True or False.")
    if never_expires:
        if expires_at is not None:
            raise BadParameterError(
                f"{operation}: pass expires_at or never_expires=True, not both."
            )
        # neverExpires: true takes no expiresAt (C38).
        return {"neverExpires": True}
    if expires_at is None:
        raise BadParameterError(
            f"{operation} needs an expiry: pass expires_at (a datetime, an ISO 8601 string with a UTC "
            f"offset, or a timedelta from now) or never_expires=True.{note}"
        )
    return {"neverExpires": False, "expiresAt": datetime_variable(expires_at, "expires_at")}


def parameters_variable(value: Mapping[str, Any], name: str) -> dict:
    """Form values for a deployment: a JSON object whose keys are the definition's ``params`` keys.

    Only the shape is checked here; the platform checks the values against the
    definition's ``params`` (unknown keys, types, required items, size).
    """
    if not isinstance(value, Mapping):
        raise BadParameterError(f"{name} must be a dict of form values (got {type(value).__name__}).")
    for key in value:
        if not isinstance(key, str):
            raise BadParameterError(f"{name} keys must be strings (got {key!r}).")
    value = dict(value)
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise BadParameterError(f"{name} must be JSON values only: {error}") from None
    return value


def model_deployment_params(dataset_id: str, deployment_id: str) -> dict:
    return {
        "datasetId": require_id(dataset_id, "dataset_id"),
        "deploymentId": require_id(deployment_id, "deployment_id"),
    }


def model_deployments_params(
    dataset_id: str,
    filter: Optional[Union[ModelDeploymentFilter, Mapping[str, Any]]] = None,
    order_by: Optional[Union[ModelDeploymentOrderBy, Mapping[str, Any]]] = None,
    cursor: Optional[str] = None,
    length: int = 20,
) -> dict:
    if not isinstance(length, int) or isinstance(length, bool) or not 1 <= length <= MAX_PAGE_LENGTH:
        raise BadParameterError(f"length must be between 1 and {MAX_PAGE_LENGTH}.")
    return {
        "datasetId": require_id(dataset_id, "dataset_id"),
        "filter": filter_variable(filter, ModelDeploymentFilter, "filter"),
        "orderBy": filter_variable(order_by, ModelDeploymentOrderBy, "order_by"),
        "cursor": cursor,
        "length": length,
    }


def create_model_deployment_params(
    dataset_id: str,
    definition_id: str,
    name: str,
    model_id: Optional[str] = None,
    description: Optional[str] = None,
    expires_at: Optional[ExpiresAt] = None,
    gpu_types: Optional[List[str]] = None,
    gpu_count: Optional[int] = None,
    invoke_timeout_seconds: Optional[int] = None,
    bind_model_to_definition: bool = False,
    parameters: Optional[Mapping[str, Any]] = None,
) -> dict:
    if not isinstance(name, str) or not name.strip():
        raise BadParameterError("name is required.")
    if isinstance(gpu_types, str):
        raise BadParameterError("gpu_types must be a list of GPU product labels, not a string.")
    if model_id is not None:
        require_id(model_id, "model_id")
    variables = {
        "datasetId": require_id(dataset_id, "dataset_id"),
        "definitionId": require_id(definition_id, "definition_id"),
        "modelId": model_id,
        "name": name,
        "description": description,
        "expiresAt": datetime_variable(expires_at, "expires_at"),
        "gpuTypes": list(gpu_types) if gpu_types is not None else None,
        "gpuCount": gpu_count,
        "invokeTimeoutSeconds": invoke_timeout_seconds,
        "bindModelToDefinition": bool(bind_model_to_definition),
    }
    # Not given: the argument is left out, so the platform fills every value with its default.
    if parameters is not None:
        variables["parameters"] = parameters_variable(parameters, "parameters")
    return variables


def update_model_deployment_params(
    dataset_id: str,
    deployment_id: str,
    name: Union[str, UndefinedType] = Undefined,
    description: Union[Optional[str], UndefinedType] = Undefined,
    invoke_timeout_seconds: Union[int, UndefinedType] = Undefined,
) -> dict:
    variables = model_deployment_params(dataset_id, deployment_id)
    if name is not Undefined:
        if not isinstance(name, str) or not name.strip():
            raise BadParameterError("name must be a non-empty string.")
        variables["name"] = name
    if description is not Undefined:
        variables["description"] = description
    if invoke_timeout_seconds is not Undefined:
        if invoke_timeout_seconds is None:
            raise BadParameterError("invoke_timeout_seconds cannot be None.")
        variables["invokeTimeoutSeconds"] = invoke_timeout_seconds
    return variables


def start_model_deployment_params(
    dataset_id: str,
    deployment_id: str,
    expires_at: Optional[ExpiresAt] = None,
    *,
    never_expires: bool = False,
) -> dict:
    variables = model_deployment_params(dataset_id, deployment_id)
    variables["expiry"] = expiry_variable(
        expires_at,
        never_expires,
        "start_model_deployment",
        # Before FDE-237 a start without expires_at kept or renewed the old expiry.
        " Starting without an expiry (keep the remaining one, renew a passed one) is no longer supported.",
    )
    return variables


def set_model_deployment_expiry_params(
    dataset_id: str,
    deployment_id: str,
    expires_at: Optional[ExpiresAt] = None,
    *,
    never_expires: bool = False,
) -> dict:
    variables = model_deployment_params(dataset_id, deployment_id)
    variables["expiry"] = expiry_variable(expires_at, never_expires, "set_model_deployment_expiry")
    return variables


def set_model_deployment_pinned_params(dataset_id: str, deployment_id: str, is_pinned: bool) -> dict:
    if not isinstance(is_pinned, bool):
        raise BadParameterError("is_pinned must be True or False.")
    variables = model_deployment_params(dataset_id, deployment_id)
    variables["isPinned"] = is_pinned
    return variables
