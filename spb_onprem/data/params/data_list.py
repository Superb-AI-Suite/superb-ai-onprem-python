from typing import (
    Optional,
    List
)
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.enums import DataType
from spb_onprem.exceptions import BadParameterError

class AnnotationFilter(CustomBaseModel):
    type: Optional[str] = None
    key: Optional[str] = None


class DataFilterOptions(CustomBaseModel):
    id_in: Optional[List[str]] = Field(None, alias="idIn")
    slice_id: Optional[str] = Field(None, alias="sliceId")
    slice_id_in: Optional[List[str]] = Field(None, alias="sliceIdIn")
    key_contains: Optional[str] = Field(None, alias="keyContains")
    key_matches: Optional[str] = Field(None, alias="keyMatches")
    type_in: Optional[List[DataType]] = Field(None, alias="typeIn")
    annotation_in: Optional[List[AnnotationFilter]] = Field(None, alias="annotationIn")
    annotation_exists: Optional[bool] = Field(None, alias="annotationExists")
    prediction_set_id_in: Optional[List[str]] = Field(None, alias="predictionSetIdIn")
    prediction_set_id_exists: Optional[bool] = Field(None, alias="predictionSetIdExists")


class DataListFilter(CustomBaseModel):
    must_filter: Optional[DataFilterOptions] = Field(None, alias="must")
    not_filter: Optional[DataFilterOptions] = Field(None, alias="not")


def get_data_id_list_params(
    dataset_id: str,
    data_list_filter: Optional[DataListFilter] = None,
    cursor: Optional[str] = None,
    length: Optional[int] = 50,
):
    """Make the variables for the dataIdList query.

    Args:
        dataset_id (str): The dataset id.
        data_list_filter (Optional[DataListFilter], optional): The filter for the data list. Defaults to None.
        cursor (Optional[str], optional): The cursor for the data list. Defaults to None.
        length (Optional[int], optional): The length of the data list. Defaults to 50.

    Raises:
        BadParameterError: The maximum length is 200.

    Returns:
        dict: The variables for the dataIdList query.
    """
    if length > 200:
        raise BadParameterError("The maximum length is 200.")

    return {
        "dataset_id": dataset_id,
        "filter": data_list_filter.model_dump(
            by_alias=True, exclude_unset=True
        ) if data_list_filter else None,
        "cursor": cursor,
        "length": length
    }


def get_data_list_params(
    dataset_id: str,
    data_list_filter: Optional[DataListFilter] = None,
    cursor: Optional[str] = None,
    length: Optional[int] = 10,
):
    """Make the variables for the dataList query.

    Args:
        dataset_id (str): The dataset id.
        data_list_filter (Optional[DataListFilter], optional): The filter for the data list. Defaults to None.
        cursor (Optional[str], optional): The cursor for the data list. Defaults to None.
        length (Optional[int], optional): The length of the data list. Defaults to 10.

    Raises:
        BadParameterError: The maximum length is 50.

    Returns:
        dict: The variables for the dataList query.
    """

    if length > 50:
        raise BadParameterError("The maximum length is 50.")

    return {
        "dataset_id": dataset_id,
        "filter": data_list_filter.model_dump(
            by_alias=True, exclude_unset=True
        ) if data_list_filter else None,
        "cursor": cursor,
        "length": length
    }
