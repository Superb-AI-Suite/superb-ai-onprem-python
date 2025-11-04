from typing import Optional, List, Union

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.base_types import Undefined, UndefinedType


class ModelsFilterOptions(CustomBaseModel):
    """Options for filtering models.
    
    Attributes:
        name_contains: Filter models by name containing this string
        id_in: Filter models by list of IDs
        is_pinned: Filter models by pinned status
        is_trained: Filter models by trained status
    """
    name_contains: Optional[str] = Field(None, alias="nameContains")
    id_in: Optional[List[str]] = Field(None, alias="idIn")
    is_pinned: Optional[bool] = Field(None, alias="isPinned")
    is_trained: Optional[bool] = Field(None, alias="isTrained")


class ModelsFilter(CustomBaseModel):
    """Filter criteria for model queries.
    
    Attributes:
        must_filter: Conditions that must be met
        not_filter: Conditions that must not be met
    """
    must_filter: Optional[ModelsFilterOptions] = Field(None, alias="must")
    not_filter: Optional[ModelsFilterOptions] = Field(None, alias="not")


def models_params(
    dataset_id: str,
    models_filter: Union[
        ModelsFilter,
        UndefinedType
    ] = Undefined,
    cursor: Optional[str] = None,
    length: Optional[int] = 10
):
    """Get parameters for listing models.
    
    Args:
        dataset_id: Required dataset ID
        models_filter: Optional filter criteria for models
        cursor: Optional cursor for pagination
        length: Optional number of items per page (default: 10)
        
    Returns:
        dict: Parameters for listing models
    """
    return {
        "datasetId": dataset_id,
        "filter": models_filter.model_dump(
            by_alias=True, exclude_unset=True
        ) if models_filter and not isinstance(models_filter, UndefinedType) else None,
        "cursor": cursor,
        "length": length
    }
