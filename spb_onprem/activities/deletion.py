"""Deletion activities.

Since 2.0.0 the SDK delete functions (``delete_models``, ``delete_diagnoses``,
``delete_analytics_reports``, ``delete_slices``, ``delete_data``,
``remove_data_from_slice`` and ``delete_dataset``) do not delete rows directly.
Each call starts one matching activity with ``startJob``, with the targets as
an ``<entity>_filter``; its progress shows in the Activity log. The singular
``delete_model``, ``delete_diagnosis``, ``delete_analytics_report`` and
``delete_slice`` are deprecated wrappers that pass one ID.

- DELETE_DATA: annotation, slice annotation, thumbnail and scene files, then the data rows.
- DELETE_SLICE: the slice's annotation files, then the slice row.
- DELETE_DATASET: model, diagnosis, analytics report, slice and data files, then the rows.
- DELETE_MODEL / DELETE_DIAGNOSIS / DELETE_ANALYTICS_REPORT: the files the entity and
  its items reference, then the item rows and the entity row.
- REMOVE_DATA_FROM_SLICE: takes the data out of the slice; it deletes no files.

The functions return the started ``ActivityHistory``. To block until it ends,
call ``ActivityService.wait_for_activity(history.id)``.

An admin of the dataset (Owner, WorkspaceAdmin or DATASET-ADMIN) starts the
activity at once. Another user with a role in the dataset submits it as
AWAITING_APPROVAL; it runs after an admin approves it.
"""
import copy
import warnings
from enum import Enum
from typing import Any, Mapping, Optional, Sequence, Tuple

from pydantic import BaseModel

from spb_onprem.exceptions import BadDeletionTargetError, BadParameterError

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

    The SDK refuses a filter without any condition. The deletion DAGs take
    ``{"must": {}}`` as "everything"; through the SDK that is never sent by
    accident.
    """
    if isinstance(value, Mapping):
        return any(has_condition(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return len(value) > 0
    if isinstance(value, str):
        return value.strip() != ""
    return value is not None


#: The platform reads an empty or blank text search as "no condition", so it
#: would select everything. Same keys as zenith and the deletion DAGs.
TEXT_MATCH_KEYS = ("nameContains", "keyContains", "titleContains")


def check_deletion_filter(value: Mapping[str, Any], filter_name: str) -> None:
    """Refuse a deletion filter that selects nothing on purpose or everything by accident.

    Refused, the same as zenith and the deletion DAGs: ``{}``, ``must: null``,
    a ``must`` that is not an object, ``must.idIn: []`` and a blank
    ``must.nameContains`` / ``keyContains`` / ``titleContains`` (empty or
    only spaces). Also refused, stricter than the DAGs: any filter without a
    condition, such as ``{"must": {}}``.

    A filter with only ``not`` (for example ``{"not": {"idIn": [x]}}``) selects
    every target except those, as on the platform.
    """
    if not value:
        raise BadDeletionTargetError(f"{filter_name} must not be empty.")
    if "must" in value:
        must = value["must"]
        if must is None:
            raise BadDeletionTargetError(f"{filter_name}.must must not be null.")
        if not isinstance(must, Mapping):
            raise BadDeletionTargetError(f"{filter_name}.must must be an object.")
        if "idIn" in must and not must["idIn"]:
            raise BadDeletionTargetError(f"{filter_name}.must.idIn must not be empty.")
        for key in TEXT_MATCH_KEYS:
            text = must.get(key)
            if isinstance(text, str) and not text.strip():
                raise BadDeletionTargetError(f"{filter_name}.must.{key} must not be blank.")
    if not has_condition(value):
        raise BadDeletionTargetError(
            f"{filter_name} has no condition. An empty filter would select every target."
        )


def deletion_filter(
    *,
    ids: Optional[Sequence[str]] = None,
    filter: Any = None,
    ids_name: str,
    filter_name: str,
    filter_types: Tuple[type, ...] = (),
    one_id: Optional[str] = None,
    one_id_name: Optional[str] = None,
) -> dict:
    """The ``<entity>_filter`` parameter of a deletion activity.

    Exactly one of ``one_id`` (when the function has one), ``ids`` and
    ``filter`` is used. IDs become ``{"must": {"idIn": [...]}}``. A filter
    model is sent with its camelCase aliases; a dict is sent as it is, so it
    must already use the GraphQL field names (an unknown field fails on the
    server instead of being dropped, which would widen the deletion).

    Raises:
        BadDeletionTargetError: When none or several targets are given, or
            they are empty. It is a BadParameterError and a ValueError.
    """
    names = [ids_name, filter_name] if one_id_name is None else [one_id_name, ids_name, filter_name]
    given = [
        name for name, value in (
            (one_id_name, one_id),
            (ids_name, ids),
            (filter_name, filter),
        )
        if name is not None and value is not None
    ]
    if len(given) != 1:
        raise BadDeletionTargetError(
            f"Pass exactly one of {', '.join(names[:-1])} or {names[-1]}"
            + (f" (got {', '.join(given)})." if given else ".")
        )

    if one_id is not None:
        if not isinstance(one_id, str) or not one_id.strip():
            raise BadDeletionTargetError(f"{one_id_name} must be a non-empty string.")
        return {"must": {"idIn": [one_id]}}

    if ids is not None:
        if isinstance(ids, (str, bytes)):
            raise BadDeletionTargetError(f"{ids_name} must be a list of IDs, not a string.")
        id_list = list(ids)
        if not id_list:
            raise BadDeletionTargetError(f"{ids_name} must not be empty.")
        if any(not isinstance(item, str) or not item.strip() for item in id_list):
            raise BadDeletionTargetError(f"{ids_name} must contain non-empty strings only.")
        return {"must": {"idIn": id_list}}

    type_names = " or ".join([t.__name__ for t in filter_types] + ["a dict"])
    if isinstance(filter, BaseModel):
        if filter_types and not isinstance(filter, filter_types):
            raise BadDeletionTargetError(f"{filter_name} must be {type_names}.")
        serialized = filter.model_dump(mode="json", by_alias=True, exclude_unset=True)
    elif isinstance(filter, Mapping):
        serialized = copy.deepcopy(dict(filter))
    else:
        raise BadDeletionTargetError(f"{filter_name} must be {type_names}.")
    check_deletion_filter(serialized, filter_name)
    return serialized


def warn_deprecated(old: str, new: str, entity: str, ids_arg: str, filter_arg: str) -> None:
    """DeprecationWarning for a singular delete function kept until the next major version.

    Calling a singular function in a loop starts one activity per target, so
    the message points to the plural function that starts a single activity.
    """
    warnings.warn(
        f"{old} is deprecated and will be removed in the next major version. "
        f"Calling it in a loop starts one deletion activity per {entity}; pass all ids "
        f"to {new}({ids_arg}=[...]) or use {filter_arg} to start a single activity.",
        DeprecationWarning,
        stacklevel=3,
    )


def start_deletion_activity(
    service,
    dataset_id: str,
    activity_type: DeletionActivityType,
    parameters: dict,
    slice_id: Optional[str] = None,
) -> ActivityHistory:
    """Start a deletion activity with ``startJob`` through ``service``.

    Args:
        service (BaseService): The service whose ``request_gql`` sends the request.
        dataset_id (str): The dataset the targets belong to.
        activity_type (DeletionActivityType): The activity to start.
        parameters (dict): The activity parameters. They must match the job
            definition's parameter schema; the server rejects other keys.
        slice_id (Optional[str]): The slice of a slice-scoped activity
            (REMOVE_DATA_FROM_SLICE). It is sent as ``startJob(sliceId)`` too,
            because the server sets the run conf's ``slice_id`` from it.

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
            slice_id=slice_id,
        ),
    )
    return ActivityHistory.model_validate(response)
