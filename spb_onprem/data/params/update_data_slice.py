from typing import Any


def update_data_slice_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
    meta: Any,
):
    """Make the variables for the updateDataSlice query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        slice_id (str): The slice ID.
        meta (Any): The meta of the data slice.
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "slice_id": slice_id,
        "meta": meta,
    } 