from typing import Any, List, Mapping, Optional, Union

from spb_onprem.activities.deletion import deletion_filter

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
    return deletion_filter(
        one_id=data_id,
        one_id_name="data_id",
        ids=data_ids,
        ids_name="data_ids",
        filter=data_filter,
        filter_name="data_filter",
        filter_types=(DataListFilter, DataFilter),
    )
