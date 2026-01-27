from typing import Optional

from spb_onprem.exceptions import BadParameterError

from .models import ModelFilter, ModelOrderBy


def get_models_params(
    dataset_id: str,
    filter: Optional[ModelFilter] = None,
    cursor: Optional[str] = None,
    length: int = 10,
):
    if length < 1 or length > 50:
        raise BadParameterError("length must be between 1 and 50.")

    return {
        "dataset_id": dataset_id,
        "filter": filter.model_dump(by_alias=True, exclude_unset=True) if filter else None,
        "order_by": None,
        "cursor": cursor,
        "length": length,
    }
