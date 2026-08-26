from typing import Union

from spb_onprem.base_types import UndefinedType, Undefined
from spb_onprem.exceptions import BadParameterError


def update_slice_params(
    dataset_id: str,
    slice_id: str,
    slice_name: Union[
        UndefinedType,
        str
    ] = Undefined,
    slice_description: Union[
        UndefinedType,
        str
    ] = Undefined
):
    """Update slice parameters.
    
    Args:
        dataset_id (str): The ID of the dataset to update the slice for.
        slice_id (str): The ID of the slice to update.
        slice_name (Optional[str]): The name of the slice to update.
        slice_description (Optional[str]): The description of the slice to update.
        
    Returns:
        dict: Parameters for slice update
    """
    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")
    if slice_id is None:
        raise BadParameterError("Slice ID is required")

    variables = {
        "dataset_id": dataset_id,
        "id": slice_id,
    }

    if slice_name is not Undefined:
        variables["name"] = slice_name
    if slice_description is not Undefined:
        variables["description"] = slice_description

    return variables
