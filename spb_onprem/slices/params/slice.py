from typing import Union

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

def slice_params(
    dataset_id: str,
    slice_id: Union[
        UndefinedType,
        str
    ] = Undefined,
    name: Union[
        UndefinedType,
        str
    ] = Undefined,
):
    """Get parameters for slice lookup.
    
    Args:
        dataset_id (str): The ID of the dataset to lookup the slice for.
        slice_id (Optional[str]): The ID of the slice to lookup.
        name (Optional[str]): The name of the slice to lookup.
        
    Returns:
        dict: Parameters for slice lookup
    """

    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")

    params = {
        "dataset_id": dataset_id,
    }
    
    if slice_id is not Undefined:
        params["id"] = slice_id
    elif name is not Undefined:
        params["name"] = name
    else:
        raise BadParameterError("Either slice_id or name must be provided.")

    return params
