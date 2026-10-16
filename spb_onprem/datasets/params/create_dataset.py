from typing import Optional, Union
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from spb_onprem.datasets.enums import DatasetType


def create_dataset_params(
    name: str,
    description: Union[
        str,
        UndefinedType,
    ] = Undefined,
    type: Union[
        Optional[DatasetType],
        UndefinedType,
    ] = Undefined,
):
    """Create parameters for dataset creation.
    
    Args:
        name: Name of the dataset(required)
        description: Optional description of the dataset
        type: Optional dataset type. Pass DatasetType.VLM for a VLM dataset;
            omit it (or pass None) for a Computer Vision dataset.
            It cannot be changed after creation.
        
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

    if type is not Undefined and type is not None:
        try:
            params["type"] = DatasetType(type).value
        except ValueError:
            raise BadParameterError(
                f"Unknown dataset type: {type!r}. "
                f"Allowed values: {[t.value for t in DatasetType]}"
            ) from None

    return params
