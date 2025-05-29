from typing import (
    Union,
    Optional,
    List
)
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)
from spb_onprem.data.entities import (
    DataMeta,
)


def update_params(
    dataset_id: str,
    data_id: str,
    key: Union[
        Optional[str],
        UndefinedType
    ] = Undefined,
    meta: Union[
        Optional[List[DataMeta]],
        UndefinedType
    ] = Undefined,
    system_meta: Union[
        Optional[List[DataMeta]],
        UndefinedType
    ] = Undefined,
):
    """Make the variables for the updateData query.

    Args:
        dataset_id (str): The dataset ID of the data.
        id (str): The ID of the data.
        key (str): The key of the data.
        meta (List[DataMeta]): The meta of the data.
        system_meta (List[DataMeta]): The system meta of the data.
    """
    variables = {
        "datasetId": dataset_id,
        "id": data_id,
    }
    
    if key is not Undefined:
        variables["key"] = key
    
    if meta is not Undefined:
        if meta is not None and not isinstance(meta, list):
            raise ValueError("meta must be a list of DataMeta or None.")
        variables["meta"] = [
            {
                "key": meta.key,
                "type": meta.type.value,
                "value": meta.value,
            }
            for meta in meta
        ] if meta is not None else None
    
    if system_meta is not Undefined:
        if system_meta is not None and not isinstance(system_meta, list):
            raise ValueError("meta must be a list of DataMeta or None.")
        variables["systemMeta"] = [
            {
                "key": meta.key,
                "type": meta.type.value,
                "value": meta.value,
            }
            for meta in system_meta
        ] if system_meta is not None else None

    return variables
