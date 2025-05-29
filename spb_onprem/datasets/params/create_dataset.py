from typing import Union
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError


def create_dataset_params(
    name: str,
    description: Union[
        str,
        UndefinedType,
    ] = Undefined,
):
    """Create parameters for dataset creation.
    
    Args:
        name: Name of the dataset(required)
        description: Optional description of the dataset
        
    Returns:
        dict: Parameters for dataset creation
    """
    if name is None:
        raise BadParameterError("Name is required")

    params = {
        "name": name,
    }

    if description is not Undefined:
        params["description"] = description

    return params
