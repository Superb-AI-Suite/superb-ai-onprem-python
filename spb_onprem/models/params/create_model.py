from typing import Optional

from spb_onprem.exceptions import BadParameterError

from ..enums import ModelTaskType


def create_model_params(
    dataset_id: str,
    name: str,
    task_type: ModelTaskType,
    description: Optional[str] = None,
    custom_dag_id: Optional[str] = None,
    total_data_count: Optional[int] = None,
    train_data_count: Optional[int] = None,
    validation_data_count: Optional[int] = None,
    training_parameters: Optional[dict] = None,
    train_slice_id: Optional[str] = None,
    validation_slice_id: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    score_key: Optional[str] = None,
    score_value: Optional[float] = None,
    score_unit: Optional[str] = None,
):
    if dataset_id is None:
        raise BadParameterError("dataset_id is required.")
    if name is None:
        raise BadParameterError("name is required.")
    if task_type is None:
        raise BadParameterError("task_type is required.")

    return {
        "dataset_id": dataset_id,
        "name": name,
        "description": description,
        "task_type": task_type.value,
        "custom_dag_id": custom_dag_id,
        "total_data_count": total_data_count,
        "train_data_count": train_data_count,
        "validation_data_count": validation_data_count,
        "training_parameters": training_parameters,
        "train_slice_id": train_slice_id,
        "validation_slice_id": validation_slice_id,
        "is_pinned": is_pinned,
        "score_key": score_key,
        "score_value": score_value,
        "score_unit": score_unit,
    }
