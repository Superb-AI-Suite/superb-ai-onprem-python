from typing import Union

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

def create_slice_params(
    dataset_id: str,
    slice_name: str,
    slice_description: Union[
        UndefinedType,
        str
    ] = Undefined,
):
    """Create parameters for slice creation.
    
    Args:
        dataset_id (str): The ID of the dataset to create the slice for.
        slice_name (str): The name of the slice to create.
        slice_description (Optional[str]): The description of the slice to create.  
        
    Returns:
        dict: Parameters for slice creation
    """

    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")
    if slice_name is None:
        raise BadParameterError("Slice name is required")

    params = {
        "dataset_id": dataset_id,
        "name": slice_name,
    }
    if slice_description is not Undefined:
        params["description"] = slice_description
    return params
