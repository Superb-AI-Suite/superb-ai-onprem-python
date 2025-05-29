from typing import (
    List, Union, Optional
)

from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)
from spb_onprem.data.entities import (
    DataMeta,
)

def remove_data_meta_params(
    dataset_id: str,
    data_id: str,
    meta: Union[
        Optional[List[DataMeta]],
        UndefinedType
    ] = Undefined,
    system_meta: Union[
        Optional[List[DataMeta]],
        UndefinedType
    ] = Undefined,
):
    """Remove meta and system meta of the selected data.

    Args:
        dataset_id (str): dataset id of the data to be removed
        data_id (str): data id to be removed
        meta (Union[ Optional[List[DataMeta]], UndefinedType ], optional): the meta to be deleted. Defaults to Undefined.
        system_meta (Union[ Optional[List[DataMeta]], UndefinedType ], optional): the system meta to be deleted. Defaults to Undefined.
    
    Returns:
        dict: the params for graphql query
    """
    
    variables = {
        "dataset_id": dataset_id,
        "data_id": data_id,
    }
    
    if meta is not Undefined:
        if meta is not None and not isinstance(meta, list):
            raise ValueError("meta must be a list of DataMeta or None.")
        variables["meta"] = [
            {
                "key": item.key,
                "type": item.type.value,
            }
            for item in meta
        ] if meta is not None else None
    
    if system_meta is not Undefined:
        if system_meta is not None and not isinstance(system_meta, list):
            raise ValueError("system_meta must be a list of DataMeta or None.")
        variables["system_meta"] = [
            {
                "key": item.key,
                "type": item.type.value,
            }
            for item in system_meta
        ] if system_meta is not None else None
    
    return variables
