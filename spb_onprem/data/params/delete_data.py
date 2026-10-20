import copy
from typing import Any, List, Mapping, Optional, Union

from pydantic import BaseModel

from spb_onprem.activities.deletion import has_condition
from spb_onprem.exceptions import BadDeletionTargetError

from .data_list import DataFilter, DataListFilter


def delete_data_params(
    dataset_id: str,
    data_id: str,
):
    """Delete the data from dataset.

    Args:
        dataset_id (str): the dataset id which the data belongs to.
        data_id (str): the data id to delete.
    """

    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
    }


def deletion_data_filter(
    data_id: Optional[str] = None,
    data_ids: Optional[List[str]] = None,
    data_filter: Optional[Union[DataListFilter, DataFilter, Mapping[str, Any]]] = None,
) -> dict:
    """The ``data_filter`` parameter of a DELETE_DATA or REMOVE_DATA_FROM_SLICE activity.

    Exactly one of the arguments is used.

    Args:
        data_id (Optional[str]): One data ID.
        data_ids (Optional[List[str]]): Several data IDs.
        data_filter (Optional[DataListFilter | dict]): A data filter. A model is
            sent with its camelCase aliases; a dict is sent as it is, so it must
            already use the GraphQL ``DataFilter`` field names (an unknown field
            fails on the server instead of being dropped).

    Raises:
        BadDeletionTargetError: When none or several of the arguments are given,
            or the IDs or the filter are empty. It is also a ValueError.

    Returns:
        dict: The filter, as the GraphQL ``DataFilter`` input.
    """
    given = [
        name for name, value in (
            ("data_id", data_id),
            ("data_ids", data_ids),
            ("data_filter", data_filter),
        )
        if value is not None
    ]
    if len(given) != 1:
        raise BadDeletionTargetError(
            "Pass exactly one of data_id, data_ids or data_filter"
            + (f" (got {', '.join(given)})." if given else ".")
        )

    if data_id is not None:
        if not isinstance(data_id, str) or not data_id.strip():
            raise BadDeletionTargetError("data_id must be a non-empty string.")
        return {"must": {"idIn": [data_id]}}

    if data_ids is not None:
        if isinstance(data_ids, (str, bytes)):
            raise BadDeletionTargetError("data_ids must be a list of IDs, not a string.")
        ids = list(data_ids)
        if not ids:
            raise BadDeletionTargetError("data_ids must not be empty.")
        if any(not isinstance(item, str) or not item.strip() for item in ids):
            raise BadDeletionTargetError("data_ids must contain non-empty strings only.")
        return {"must": {"idIn": ids}}

    if isinstance(data_filter, BaseModel):
        serialized = data_filter.model_dump(mode="json", by_alias=True, exclude_unset=True)
    elif isinstance(data_filter, Mapping):
        serialized = copy.deepcopy(dict(data_filter))
    else:
        raise BadDeletionTargetError("data_filter must be a DataListFilter or a dict.")
    if not has_condition(serialized):
        raise BadDeletionTargetError(
            "data_filter has no condition. An empty filter would select the whole dataset."
        )
    return serialized
