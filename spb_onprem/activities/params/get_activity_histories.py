from typing import Any, Dict, List, Optional, Union

from spb_onprem.activities.entities import ActivityStatus
from spb_onprem.exceptions import BadParameterError

#: The platform's ``jobHistories`` takes ``length`` from 1 to 50.
MAX_ACTIVITY_HISTORIES_LENGTH = 50


def _string_list(value: Union[str, List[str]], name: str) -> List[str]:
    """One string or a list of strings, as a non-empty list of non-empty strings.

    An empty list is refused: the platform reads it as "no condition" and would
    list every run of the dataset.
    """
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, (list, tuple, set, frozenset)):
        raise BadParameterError(f"{name} must be a string or a list of strings.")
    values = list(values)
    if not values:
        raise BadParameterError(f"{name} must not be an empty list; leave it out to not filter.")
    for item in values:
        if not isinstance(item, str) or not item.strip():
            raise BadParameterError(f"{name} must hold non-empty strings (got {item!r}).")
    return values


def _status_list(
    value: Union[ActivityStatus, str, List[Union[ActivityStatus, str]]],
) -> List[str]:
    values = [value] if isinstance(value, (str, ActivityStatus)) else value
    if not isinstance(values, (list, tuple, set, frozenset)):
        raise BadParameterError("status must be an ActivityStatus, its name, or a list of them.")
    values = list(values)
    if not values:
        raise BadParameterError("status must not be an empty list; leave it out to not filter.")
    statuses = []
    for item in values:
        try:
            status = ActivityStatus(item)
        except ValueError:
            raise BadParameterError(
                f"status must be one of {[s.value for s in ActivityStatus]} (got {item!r})."
            ) from None
        if status.value not in statuses:
            statuses.append(status.value)
    return statuses


def get_activity_histories_params(
    dataset_id: str,
    activity_id: Optional[Union[str, List[str]]] = None,
    status: Optional[Union[ActivityStatus, str, List[Union[ActivityStatus, str]]]] = None,
    requester: Optional[Union[str, List[str]]] = None,
    slice_id: Optional[Union[str, List[str]]] = None,
    cursor: Optional[str] = None,
    length: int = 10,
    oldest_first: bool = False,
) -> Dict[str, Any]:
    """Variables of the ``jobHistories`` query.

    The dataset is sent twice: as the ``datasetId`` argument (the platform
    checks the caller's permission on it) and as ``filter.must.datasetId`` (the
    condition the list is read with). Each other condition goes into
    ``filter.must`` only when given.
    """
    if not isinstance(dataset_id, str) or not dataset_id.strip():
        raise BadParameterError("dataset_id is required.")
    if not isinstance(length, int) or isinstance(length, bool) or not 1 <= length <= MAX_ACTIVITY_HISTORIES_LENGTH:
        raise BadParameterError(f"length must be between 1 and {MAX_ACTIVITY_HISTORIES_LENGTH}.")
    if cursor is not None and not isinstance(cursor, str):
        raise BadParameterError("cursor must be the next cursor of the previous page (a string).")
    if not isinstance(oldest_first, bool):
        raise BadParameterError("oldest_first must be True or False.")

    must: Dict[str, Any] = {"datasetId": dataset_id}
    if activity_id is not None:
        must["jobIdIn"] = _string_list(activity_id, "activity_id")
    if status is not None:
        must["statusIn"] = _status_list(status)
    if requester is not None:
        must["requestedByIn"] = _string_list(requester, "requester")
    if slice_id is not None:
        must["sliceIdIn"] = _string_list(slice_id, "slice_id")

    return {
        "datasetId": dataset_id,
        "filter": {"must": must},
        "orderBy": {"field": "createdAt", "direction": "ASC" if oldest_first else "DESC"},
        "cursor": cursor,
        "length": length,
    }
