from typing import (
    Union,
    Optional,
    List
)
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

class SlicesFilterOptions(CustomBaseModel):
    """Options for filtering slices.
    
    Attributes:
        name_contains: Filter slices by name containing this string
        id_in: Filter slices by list of IDs
    """
    name_contains: Optional[str] = Field(None, alias="nameContains")
    id_in: Optional[List[str]] = Field(None, alias="idIn")


class SlicesFilter(CustomBaseModel):
    """Filter criteria for slice queries.
    
    Attributes:
        must_filter: Conditions that must be met
        not_filter: Conditions that must not be met
    """
    must_filter: Optional[SlicesFilterOptions] = Field(None, alias="must")
    not_filter: Optional[SlicesFilterOptions] = Field(None, alias="not")


def slices_params(
    dataset_id: str,
    slices_filter: Union[
        UndefinedType,
        SlicesFilter
    ] = Undefined,
    cursor: Optional[str] = None,
    length: Optional[int] = 10
):
    """Get the params for the slices query.

    Args:
        dataset_id (str): the dataset id to get the slices for.
        slices_filter (Union[ UndefinedType, SlicesFilter ]): the filter for the slices.
        cursor (Optional[str], optional): The next cursor to get the next page of slices. Defaults to None.
        length (Optional[int], optional): The number of slices to get. Defaults to 10.
    """

    if dataset_id is None:
        raise BadParameterError("Dataset ID is required")
    params = {
        "dataset_id": dataset_id,
        "cursor": cursor,
        "length": length,
    }
    if slices_filter is not Undefined and slices_filter is not None:
        params["filter"] = slices_filter.model_dump(
            by_alias=True, exclude_unset=True
        )

    return params
