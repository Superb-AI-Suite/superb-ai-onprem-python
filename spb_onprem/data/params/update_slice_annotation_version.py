from typing import Union, Optional, Any, List
from spb_onprem.base_types import UndefinedType, Undefined
from spb_onprem.exceptions import BadParameterError


def update_slice_annotation_version_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
    id: str,
    channels: Union[List[str], UndefinedType, None] = Undefined,
    version: Union[str, UndefinedType, None] = Undefined,
    meta: Union[dict, UndefinedType, None] = Undefined,
):
    """Make the variables for the updateSliceAnnotationVersion query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        slice_id (str): The slice ID.
        id (str): The annotation version ID.
        channels (list[str], optional): The channels of the annotation version.
        version (str, optional): The version string of the annotation version.
        meta (dict, optional): The meta of the annotation version.
    """
    variables = {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "slice_id": slice_id,
        "id": id,
    }

    if channels is not Undefined:
        variables["channels"] = channels
    if version is not Undefined:
        variables["version"] = version
    if meta is not Undefined:
        variables["meta"] = meta

    return variables 