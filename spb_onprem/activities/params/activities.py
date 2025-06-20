from typing import (
    Union,
    Optional,
    List,
)

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.base_types import Undefined, UndefinedType


class ActivitiesFilterOptions(CustomBaseModel):
    """Options for filtering activities.
    
    """
    id_in: Optional[List[str]] = Field(None, alias="idIn")
    name_contains: Optional[str] = Field(None, alias="nameContains")
    dataset_id_in: Optional[List[str]] = Field(None, alias="datasetIdIn")
    type_in: Optional[List[str]] = Field(None, alias="typeIn")


class ActivitiesFilter(CustomBaseModel):
    """Filter criteria for activity queries.
    
    Attributes:
        must_filter: Conditions that must be met
        not_filter: Conditions that must not be met
    """
    must_filter: Optional[ActivitiesFilterOptions] = Field(None, alias="must")
    not_filter: Optional[ActivitiesFilterOptions] = Field(None, alias="not")


def get_activities_params(
    dataset_id: str,
    activity_filter: Union[
        UndefinedType,
        ActivitiesFilter,
    ] = Undefined,
    cursor: Optional[str] = None,
    length: Optional[int] = 10
):
    """Get the params for the activities query.
    
    """
    params = {
        "datasetId": dataset_id,
        "cursor": cursor,
        "length": length,
    }
    if activity_filter is not Undefined and activity_filter is not None:
        params["filter"] = activity_filter.model_dump(
            by_alias=True, exclude_unset=True
        )
    return params