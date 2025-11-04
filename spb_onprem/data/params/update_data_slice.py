from typing import Any, Optional, Union, List
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)
from spb_onprem.data.entities import (
    DataAnnotationStat,
)


def update_data_slice_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
    meta: Union[
        Optional[dict],
        UndefinedType
    ] = Undefined,
    annotation_stats: Union[
        Optional[List[DataAnnotationStat]],
        UndefinedType
    ] = Undefined
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

    if annotation_stats is not Undefined:
        params["annotation_stats"] = [
            stat.model_dump(by_alias=True, exclude_unset=True) for stat in annotation_stats
        ] if annotation_stats is not None else None

    if meta is not Undefined:
        params["meta"] = meta

    return params