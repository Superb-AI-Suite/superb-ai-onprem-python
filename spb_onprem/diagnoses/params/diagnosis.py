from typing import Union

from spb_onprem.base_types import Undefined, UndefinedType


def get_diagnosis_params(
    dataset_id: str,
    diagnosis_id: Union[str, UndefinedType] = Undefined,
    name: Union[str, UndefinedType] = Undefined,
):
    params = {
        "dataset_id": dataset_id,
    }
    if diagnosis_id is not Undefined:
        params["diagnosis_id"] = diagnosis_id
    if name is not Undefined:
        params["name"] = name
    return params
