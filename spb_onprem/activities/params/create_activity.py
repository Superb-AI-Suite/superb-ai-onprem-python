from typing import Union, List

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.activities.entities import ActivitySchema
from spb_onprem.exceptions import BadParameterError

def create_activity_params(
    activity_type: str,
    name: str,
    dataset_id: Union[
        UndefinedType,
        str
    ] = Undefined,
    description: Union[
        UndefinedType,
        str
    ] = Undefined,
    progress_schema: Union[
        UndefinedType,
        List[ActivitySchema]
    ] = Undefined,
    parameter_schema: Union[
        UndefinedType,
        List[ActivitySchema]
    ] = Undefined,
    settings: Union[
        UndefinedType,
        dict
    ] = Undefined,
    meta: Union[
        UndefinedType,
        dict
    ] = Undefined,
):
    """Create parameters for activity creation.
    
    Args:
        activity_type (str): The type of the activity to create.
        name (str): The name of the activity to create.
        dataset_id (Optional[str]): The ID of the dataset to create the activity for.
        description (Optional[str]): The description of the activity to create.
        progress_schema (Optional[List[ActivitySchema]]): The progress schema of the activity to create.
        parameter_schema (Optional[List[ActivitySchema]]): The parameter schema of the activity to create.
        settings (Optional[dict]): The settings of the activity to create.
        meta (Optional[dict]): The meta of the activity to create.
        
    Returns:
        dict: Parameters for activity creation
        
    Raises:
        BadParameterError: If activity_type is not provided
    """
    if activity_type is None:
        raise BadParameterError("Activity type is required")
    if name is None:
        raise BadParameterError("Activity name is required")

    params = {
        "datasetId": None,
        "name": name,
        "description": None,
        "progressSchema": None,
        "parameterSchema": None,
        "type": activity_type,
        "settings": None,
        "meta": None,
    }
    if dataset_id is not Undefined:
        params["datasetId"] = dataset_id
    if description is not Undefined:
        params["description"] = description
    if progress_schema is not Undefined:
        params["progressSchema"] = progress_schema
    if parameter_schema is not Undefined:
        params["parameterSchema"] = parameter_schema
    if settings is not Undefined:
        params["settings"] = settings
    if meta is not Undefined:
        params["meta"] = meta
    return params
