from typing import Union
from spb_onprem.base_types import UndefinedType, Undefined
from spb_onprem.exceptions import BadParameterError

def update_annotation_params(
    dataset_id: str,
    data_id: str,
    meta: Union[
        dict,
        UndefinedType,
    ],
):
    """Make the variables for the updateAnnotation query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        meta (dict): The meta of the data.
    """
    variables = {
        "dataset_id": dataset_id,
        "data_id": data_id,
    }

    if meta is not Undefined:
        if meta is not None and not isinstance(meta, dict):
            raise BadParameterError("meta must be a dict or None.")
        variables["meta"] = meta

    return variables
