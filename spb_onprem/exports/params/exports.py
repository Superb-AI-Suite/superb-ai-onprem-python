from typing import Optional, List, Union
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError


class ExportFilterOptions(CustomBaseModel):
    """Options for filtering exports.
    
    Attributes:
        id_in: Filter exports by list of IDs
        name_contains: Filter exports by name containing this string
        name: Filter exports by exact name match
        location_contains: Filter exports by location containing this string
        location: Filter exports by exact location match
    """
    id_in: Optional[List[str]] = Field(None, alias="idIn")
    name_contains: Optional[str] = Field(None, alias="nameContains")
    name: Optional[str] = Field(None, alias="name")
    location_contains: Optional[str] = Field(None, alias="locationContains")
    location: Optional[str] = Field(None, alias="location")


class ExportFilter(CustomBaseModel):
    """Filter criteria for export queries.
    
    Attributes:
        must_filter: Conditions that must be met
        not_filter: Conditions that must not be met
    """
    must_filter: Optional[ExportFilterOptions] = Field(None, alias="must")
    not_filter: Optional[ExportFilterOptions] = Field(None, alias="not")


def get_exports_params(
    dataset_id: str,
    export_filter: Union[
        UndefinedType,
        ExportFilter
    ] = Undefined,
    cursor: Union[
        UndefinedType,
        str
    ] = Undefined,
    length: int = 10,
):
    """Create parameters for getting exports.
    
    Args:
        dataset_id (str): The ID of the dataset to get exports for.
        export_filter (Optional[ExportFilter]): The filter to apply to the exports.
        cursor (Optional[str]): The cursor to use for pagination.
        length (int): The number of exports to get.
        
    Returns:
        dict: Parameters for getting exports
        
    Raises:
        BadParameterError: If dataset_id is missing
    """
    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")

    params = {
        "dataset_id": dataset_id,
        "length": length
    }

    if export_filter is not Undefined and export_filter is not None:
        params["filter"] = export_filter.model_dump(by_alias=True, exclude_unset=True)
    if cursor is not Undefined:
        params["cursor"] = cursor

    return params 