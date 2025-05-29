from typing import Optional, List, Union

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.base_types import Undefined, UndefinedType


class DatasetsFilterOptions(CustomBaseModel):
    """Options for filtering datasets.
    
    Attributes:
        name_contains: Filter datasets by name containing this string
        id_in: Filter datasets by list of IDs
    """
    name_contains: Optional[str] = Field(None, alias="nameContains")
    id_in: Optional[List[str]] = Field(None, alias="idIn")


class DatasetsFilter(CustomBaseModel):
    """Filter criteria for dataset queries.
    
    Attributes:
        must_filter: Conditions that must be met
        not_filter: Conditions that must not be met
    """
    must_filter: Optional[DatasetsFilterOptions] = Field(None, alias="must")
    not_filter: Optional[DatasetsFilterOptions] = Field(None, alias="not")


def datasets_params(
    datasets_filter: Union[
        DatasetsFilter,
        UndefinedType
    ] = Undefined,
    cursor: Optional[str] = None,
    length: Optional[int] = 10
):
    """Get parameters for listing datasets.
    
    Args:
        datasets_filter: Optional filter criteria for datasets
        cursor: Optional cursor for pagination
        length: Optional number of items per page (default: 10)
        
    Returns:
        dict: Parameters for listing datasets
    """
    return {
        "filter": datasets_filter.model_dump(
            by_alias=True, exclude_unset=True
        ) if datasets_filter else None,
        "cursor": cursor,
        "length": length
    }
