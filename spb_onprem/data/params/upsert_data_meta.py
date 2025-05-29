from typing import List, Union, Optional

from spb_onprem.data.entities import DataMeta
from spb_onprem.base_types import UndefinedType, Undefined


def upsert_data_meta_params(
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
    """Make the variables for the upsertDataMeta query.

    Args:
        dataset_id (str): The dataset ID of the data.
        id (str): The ID of the data.
        meta (List[DataMeta]): The meta of the data.
        system_meta (List[DataMeta]): The system meta of the data.
    """
    variables = {
        "dataset_id": dataset_id,
        "data_id": data_id,
    }

    if meta is not Undefined:
        if meta is not None and not isinstance(meta, list):
            raise ValueError("meta must be a list of DataMeta or None.")
        variables["meta"] = [
            item.model_dump(by_alias=True, exclude_unset=True)
            for item in meta
        ] if meta is not None else None

    if system_meta is not Undefined:
        if system_meta is not None and not isinstance(system_meta, list):
            raise ValueError("system_meta must be a list of DataMeta or None.")
        variables["system_meta"] = [
            item.model_dump(by_alias=True, exclude_unset=True)
            for item in system_meta
        ] if system_meta is not None else None

    return variables
