from typing import Optional
import re

from spb_onprem.exceptions import BadParameterError

from ..enums import ModelTaskType
from ..entities import TrainingAnnotations


def create_model_params(
    dataset_id: str,
    name: str,
    task_type: ModelTaskType,
    description: Optional[str] = None,
    custom_dag_id: Optional[str] = None,
    total_data_count: Optional[int] = None,
    train_data_count: Optional[int] = None,
    validation_data_count: Optional[int] = None,
    training_annotations: Optional[list[TrainingAnnotations]] = None,
    training_parameters: Optional[dict] = None,
    train_slice_id: Optional[str] = None,
    validation_slice_id: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    score_key: Optional[str] = None,
    score_value: Optional[float] = None,
    score_unit: Optional[str] = None,
    contents: Optional[dict] = None,
):
    if dataset_id is None:
        raise BadParameterError("dataset_id is required.")
    if name is None:
        raise BadParameterError("name is required.")
    if task_type is None:
        raise BadParameterError("task_type is required.")
    
    if training_annotations is not None:
        if not isinstance(training_annotations, list):
            raise BadParameterError("training_annotations must be a list.")
        
        for annotation in training_annotations:
            if not isinstance(annotation, TrainingAnnotations):
                raise BadParameterError("Each item in training_annotations must be a TrainingAnnotations instance.")
    
    if contents is not None:
        if not isinstance(contents, dict):
            raise BadParameterError("contents must be a dictionary.")
        
        ulid_pattern = re.compile(r'^[0-9A-Z]{26}$')
        
        for file_name, content_id in contents.items():
            if not isinstance(file_name, str):
                raise BadParameterError("All keys in contents must be strings (file names).")
            
            if not isinstance(content_id, str):
                raise BadParameterError(f"Value for '{file_name}' in contents must be a string (content ID).")
            
            if not ulid_pattern.match(content_id):
                raise BadParameterError(f"Value for '{file_name}' in contents must be a valid ULID format (26 uppercase alphanumeric characters).")

    return {
        "dataset_id": dataset_id,
        "name": name,
        "description": description,
        "task_type": task_type.value,
        "custom_dag_id": custom_dag_id,
        "total_data_count": total_data_count,
        "train_data_count": train_data_count,
        "validation_data_count": validation_data_count,
        "training_annotations": [annotation.model_dump(by_alias=True, exclude_none=True) for annotation in training_annotations] if training_annotations else None,
        "training_parameters": training_parameters,
        "train_slice_id": train_slice_id,
        "validation_slice_id": validation_slice_id,
        "is_pinned": is_pinned,
        "score_key": score_key,
        "score_value": score_value,
        "score_unit": score_unit,
        "contents": contents,
    }
