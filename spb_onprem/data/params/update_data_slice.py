from typing import Any, Optional, Union
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)


def update_data_slice_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
    meta: Union[
        Optional[dict],
        UndefinedType
    ] = Undefined,
):
    """Make the variables for the updateDataSlice query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        slice_id (str): The slice ID.
        meta (dict): The meta of the data slice.
    """
    params = {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "slice_id": slice_id,
    }
    
    if meta is not Undefined:
        params["meta"] = meta

    return params