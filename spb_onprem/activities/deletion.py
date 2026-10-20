"""Deletion activities.

Since 2.0.0 the SDK delete functions (``delete_model``, ``delete_diagnosis``,
``delete_analytics_report``, ``delete_dataset``, ``delete_data``,
``delete_slice`` and ``remove_data_from_slice``) do not delete rows directly.
They start the matching activity with ``startJob``. The activity deletes the
rows and the files in storage, and its progress shows in the Activity log.

The functions return the started ``ActivityHistory``. To block until it ends,
call ``ActivityService.wait_for_activity(history.id)``.

An admin of the dataset (Owner, WorkspaceAdmin or DATASET-ADMIN) starts the
activity at once. Another user with a role in the dataset submits it as
AWAITING_APPROVAL; it runs after an admin approves it.
"""
from enum import Enum
from typing import Any, Mapping, Optional

from spb_onprem.exceptions import BadParameterError

from .entities import ActivityHistory
from .queries import Queries


class DeletionActivityType(str, Enum):
    """Activity (job) types that delete platform entities."""

    DELETE_MODEL = "DELETE_MODEL"
    DELETE_DIAGNOSIS = "DELETE_DIAGNOSIS"
    DELETE_ANALYTICS_REPORT = "DELETE_ANALYTICS_REPORT"
    DELETE_DATASET = "DELETE_DATASET"
    DELETE_DATA = "DELETE_DATA"
    DELETE_SLICE = "DELETE_SLICE"
    REMOVE_DATA_FROM_SLICE = "REMOVE_DATA_FROM_SLICE"


def require_id(value: Optional[str], name: str) -> str:
    """Raise BadParameterError when a required ID is missing or empty."""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise BadParameterError(f"{name} is required.")
    return value


def has_condition(value: Any) -> bool:
    """True when a filter value narrows the selection.

    Same rule as the deletion DAGs: an empty filter would select everything.
    """
    if isinstance(value, Mapping):
        return any(has_condition(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return len(value) > 0
    return value is not None and value != ""


def start_deletion_activity(
    service,
    dataset_id: str,
    activity_type: DeletionActivityType,
    parameters: dict,
) -> ActivityHistory:
    """Start a deletion activity with ``startJob`` through ``service``.

    Args:
        service (BaseService): The service whose ``request_gql`` sends the request.
        dataset_id (str): The dataset the targets belong to.
        activity_type (DeletionActivityType): The activity to start.
        parameters (dict): The activity parameters. They must match the job
            definition's parameter schema; the server rejects other keys.

    Returns:
        ActivityHistory: The started activity. Its status is PENDING, or
        AWAITING_APPROVAL when the request needs a dataset admin's approval.
    """
    response = service.request_gql(
        Queries.START_ACTIVITY,
        Queries.START_ACTIVITY["variables"](
            dataset_id=dataset_id,
            activity_type=DeletionActivityType(activity_type).value,
            parameters=parameters,
        ),
    )
    return ActivityHistory.model_validate(response)
