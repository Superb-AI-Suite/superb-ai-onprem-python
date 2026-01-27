from typing import Optional, Union
import re

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

from ..enums import ModelStatus, ModelTaskType
from ..entities import TrainingAnnotations


def update_model_params(
    dataset_id: str,
    model_id: str,
    name: Union[Optional[str], UndefinedType] = Undefined,
    description: Union[Optional[str], UndefinedType] = Undefined,
    status: Union[Optional[ModelStatus], UndefinedType] = Undefined,
    task_type: Union[Optional[ModelTaskType], UndefinedType] = Undefined,
    custom_dag_id: Union[Optional[str], UndefinedType] = Undefined,
    total_data_count: Union[Optional[int], UndefinedType] = Undefined,
    train_data_count: Union[Optional[int], UndefinedType] = Undefined,
    validation_data_count: Union[Optional[int], UndefinedType] = Undefined,
    training_annotations: Union[Optional[list[TrainingAnnotations]], UndefinedType] = Undefined,
    training_parameters: Union[Optional[dict], UndefinedType] = Undefined,
    train_slice_id: Union[Optional[str], UndefinedType] = Undefined,
    validation_slice_id: Union[Optional[str], UndefinedType] = Undefined,
    is_pinned: Union[Optional[bool], UndefinedType] = Undefined,
    score_key: Union[Optional[str], UndefinedType] = Undefined,
    score_value: Union[Optional[float], UndefinedType] = Undefined,
    score_unit: Union[Optional[str], UndefinedType] = Undefined,
    contents: Union[Optional[dict], UndefinedType] = Undefined,
):
    # Validate training_annotations if provided
    if training_annotations is not Undefined and training_annotations is not None:
        if not isinstance(training_annotations, list):
            raise BadParameterError("training_annotations must be a list.")
        
        for annotation in training_annotations:
            if not isinstance(annotation, TrainingAnnotations):
                raise BadParameterError("Each item in training_annotations must be a TrainingAnnotations instance.")
    
    # Validate contents if provided
    if contents is not Undefined and contents is not None:
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
    
    variables = {
        "dataset_id": dataset_id,
        "model_id": model_id,
    }

    if name is not Undefined:
        variables["name"] = name
    if description is not Undefined:
        variables["description"] = description
    if status is not Undefined:
        variables["status"] = status.value if status is not None else None
    if task_type is not Undefined:
        variables["task_type"] = task_type.value if task_type is not None else None
    if custom_dag_id is not Undefined:
        variables["custom_dag_id"] = custom_dag_id
    if total_data_count is not Undefined:
        variables["total_data_count"] = total_data_count
    if train_data_count is not Undefined:
        variables["train_data_count"] = train_data_count
    if validation_data_count is not Undefined:
        variables["validation_data_count"] = validation_data_count
    if training_annotations is not Undefined:
        variables["training_annotations"] = [annotation.model_dump(by_alias=True, exclude_none=True) for annotation in training_annotations] if training_annotations else None
    if training_parameters is not Undefined:
        variables["training_parameters"] = training_parameters
    if train_slice_id is not Undefined:
        variables["train_slice_id"] = train_slice_id
    if validation_slice_id is not Undefined:
        variables["validation_slice_id"] = validation_slice_id
    if is_pinned is not Undefined:
        variables["is_pinned"] = is_pinned
    if score_key is not Undefined:
        variables["score_key"] = score_key
    if score_value is not Undefined:
        variables["score_value"] = score_value
    if score_unit is not Undefined:
        variables["score_unit"] = score_unit
    if contents is not Undefined:
        variables["contents"] = contents

    return variables
