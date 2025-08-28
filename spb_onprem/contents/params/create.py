from typing import Union
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)


def create_variables(
    key: Union[str, UndefinedType] = Undefined,
    content_type: Union[str, UndefinedType] = Undefined,
):
    params = {}
    
    if key is not Undefined:
        params["key"] = key
    if content_type is not Undefined:
        params["content_type"] = content_type
    return params