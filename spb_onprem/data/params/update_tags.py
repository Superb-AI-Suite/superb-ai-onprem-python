from typing import (
    Union,
    Optional,
    List
)
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)


def update_tags_params(
    dataset_id: str,
    slice_id: str,
    data_id: str,
    tags: Union[
        Optional[List[str]],
        UndefinedType
    ] = Undefined,
):
    """Make the variables for the updateDataTags mutation.

    Args:
        dataset_id (str): The dataset ID of the data.
        slice_id (str): The slice ID.
        data_id (str): The ID of the data.
        tags (List[str]): The list of tags to update.
    """
    variables = {
        "datasetId": dataset_id,
        "sliceId": slice_id,
        "dataId": data_id,
    }
    
    if tags is not Undefined:
        variables["tags"] = tags
    
    return variables
