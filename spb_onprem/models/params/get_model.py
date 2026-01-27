from typing import Union

from spb_onprem.base_types import Undefined, UndefinedType


def get_model_params(
    dataset_id: str,
    model_id: Union[str, UndefinedType] = Undefined,
    name: Union[str, UndefinedType] = Undefined,
):
    params = {
        "dataset_id": dataset_id,
    }

    if model_id is not Undefined:
        params["model_id"] = model_id

    if name is not Undefined:
        params["name"] = name

    return params
