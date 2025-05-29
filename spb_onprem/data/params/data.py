from typing import Union
from spb_onprem.base_types import Undefined, UndefinedType


def get_params(
    dataset_id: str,
    data_id: Union[str, UndefinedType] = Undefined,
    data_key: Union[str, UndefinedType] = Undefined,
):
    """Make the variables for the data query.

    Args:
        data_id (Union[str, UndefinedType], optional): The ID of the data. Defaults to Undefined.
        data_key (Union[str, UndefinedType], optional): The key of the data. Defaults to Undefined.

    Returns:
        dict: The variables for the data query.
    """
    
    return {
        "dataset_id": dataset_id,
        "key": data_key,
        "id": data_id,
    }
