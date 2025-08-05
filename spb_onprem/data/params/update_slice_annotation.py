from typing import Union, Any
from spb_onprem.base_types import UndefinedType, Undefined


def update_slice_annotation_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
    meta: Any,
):
    """Make the variables for the updateSliceAnnotation query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        slice_id (str): The slice ID.
        meta (Any): The meta of the slice annotation.
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "slice_id": slice_id,
        "meta": meta,
    } 