from typing import Union, List

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from spb_onprem.activities.entities import ActivitySchema

def update_activity_params(
    activity_id: str,
    dataset_id: Union[
        str,
        UndefinedType
    ] = Undefined,
    activity_type: Union[
        str,
        UndefinedType
    ] = Undefined,
    name: Union[
        str,
        UndefinedType
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
    """Create parameters for activity update.
    
    Args:
        activity_id (str): The ID of the activity to update.
        activity_type (Optional[str]): The type of the activity to update.
        name (Optional[str]): The name of the activity to update.
        dataset_id (Optional[str]): The ID of the dataset to update the activity for.
        description (Optional[str]): The description of the activity to update.
        progress_schema (Optional[List[ActivitySchema]]): The progress schema of the activity to update.
        parameter_schema (Optional[List[ActivitySchema]]): The parameter schema of the activity to update.
        settings (Optional[dict]): The settings of the activity to update.
        meta (Optional[dict]): The meta of the activity to update.
        
    Returns:
        dict: Parameters for activity update
        
    Raises:
        BadParameterError: If activity_id is not provided
    """
    if activity_id is None:
        raise BadParameterError("Activity ID is required")

    params = {
        "id": activity_id
    }

    if dataset_id is not Undefined:
        params["datasetId"] = dataset_id
    if activity_type is not Undefined:
        params["type"] = activity_type
    if name is not Undefined:
        params["name"] = name
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
