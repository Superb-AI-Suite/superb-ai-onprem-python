from typing import Union

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError


def update_dataset_params(
    dataset_id: str,
    name: Union[
        str,
        UndefinedType,
    ] = Undefined,
    description: Union[
        str,
        UndefinedType,
    ] = Undefined,
):
    """Update parameters for dataset modification.
    
    Args:
        id: ID of the dataset to update
        name: Optional new name for the dataset
        description: Optional new description for the dataset
        
    Returns:
        dict: Parameters for dataset update
    """
    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")

    params = {
        "id": dataset_id,
    }

    if name is not Undefined:
        params["name"] = name
    if description is not Undefined:
        params["description"] = description
    return params
