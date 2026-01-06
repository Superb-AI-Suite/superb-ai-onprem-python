from typing import Union, List
from spb_onprem.base_types import UndefinedType, Undefined


def update_annotation_version_params(
    dataset_id: str,
    data_id: str,
    version_id: str,
    channels: Union[List[str], UndefinedType, None] = Undefined,
    version: Union[str, UndefinedType, None] = Undefined,
    meta: Union[dict, UndefinedType, None] = Undefined,
    content_id: Union[str, UndefinedType, None] = Undefined,
):
    """Make the variables for the updateAnnotationVersion query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        id (str): The annotation version ID.
        channels (list[str], optional): The channels of the annotation version.
        version (str, optional): The version string of the annotation version.
        meta (dict, optional): The meta of the annotation version.
    """
    variables = {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "version_id": version_id,
    }

    if channels is not Undefined:
        variables["channels"] = channels
    if version is not Undefined:
        variables["version"] = version
    if meta is not Undefined:
        variables["meta"] = meta
    if content_id is not Undefined:
        variables["content_id"] = content_id

    return variables
