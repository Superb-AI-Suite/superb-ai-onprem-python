from datetime import datetime, timedelta, timezone
from typing import Any, List, Mapping, Optional, Union

from spb_onprem.activities.deletion import require_id
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

from .filters import ModelDeploymentFilter, ModelDeploymentOrderBy, filter_variable

#: An absolute time, or how long from now.
ExpiresAt = Union[datetime, timedelta, str]

#: The platform returns at most this many deployments per page.
MAX_PAGE_LENGTH = 100


def datetime_variable(value: Optional[ExpiresAt], name: str) -> Optional[str]:
    """An ISO 8601 UTC time for a GraphQL DateTime.

    A ``timedelta`` is counted from now. A naive ``datetime`` is local time.
    A ``str`` is sent as it is.
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
        return value
    raise BadParameterError(f"{name} must be a datetime, a timedelta or an ISO 8601 string.")


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
) -> dict:
    if not isinstance(name, str) or not name.strip():
        raise BadParameterError("name is required.")
    if isinstance(gpu_types, str):
        raise BadParameterError("gpu_types must be a list of GPU product labels, not a string.")
    if model_id is not None:
        require_id(model_id, "model_id")
    return {
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
) -> dict:
    variables = model_deployment_params(dataset_id, deployment_id)
    variables["expiresAt"] = datetime_variable(expires_at, "expires_at")
    return variables


def set_model_deployment_pinned_params(dataset_id: str, deployment_id: str, is_pinned: bool) -> dict:
    if not isinstance(is_pinned, bool):
        raise BadParameterError("is_pinned must be True or False.")
    variables = model_deployment_params(dataset_id, deployment_id)
    variables["isPinned"] = is_pinned
    return variables
