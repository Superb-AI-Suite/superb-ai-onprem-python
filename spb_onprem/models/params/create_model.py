from typing import List, Union, Any, Optional
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.models.entities.model_train_class import ModelTrainClass


def create_model_params(
    dataset_id: str,
    name: str,
    baseline_model: str,
    training_slice_ids: List[str],
    validation_slice_ids: List[str],
    description: Union[str, UndefinedType] = Undefined,
    training_classes: Union[List[ModelTrainClass], UndefinedType] = Undefined,
    model_content_id: Union[str, UndefinedType] = Undefined,
    is_trained: Union[bool, UndefinedType] = Undefined,
    trained_at: Union[str, UndefinedType] = Undefined,
    is_pinned: Union[bool, UndefinedType] = Undefined,
    meta: Union[Any, UndefinedType] = Undefined,
):
    """Get parameters for creating a model.
    
    Args:
        dataset_id: The dataset ID
        name: The model name
        baseline_model: The baseline model used
        training_slice_ids: The IDs of the training slices
        validation_slice_ids: The IDs of the validation slices
        description: Optional model description
        training_classes: Optional training classes
        model_content_id: Optional model content ID
        is_trained: Optional trained status
        trained_at: Optional trained timestamp
        is_pinned: Optional pinned status
        meta: Optional metadata
        
    Returns:
        dict: Parameters for creating a model
    """
    params = {
        "datasetId": dataset_id,
        "name": name,
        "baselineModel": baseline_model,
        "trainingSliceIds": training_slice_ids,
        "validationSliceIds": validation_slice_ids,
    }
    
    if not isinstance(description, UndefinedType):
        params["description"] = description
    
    if not isinstance(training_classes, UndefinedType):
        params["trainingClasses"] = [
            tc.model_dump(by_alias=True, exclude_unset=True) for tc in training_classes
        ] if training_classes is not None else None
    
    if not isinstance(model_content_id, UndefinedType):
        params["modelContentId"] = model_content_id
    
    if not isinstance(is_trained, UndefinedType):
        params["isTrained"] = is_trained
    
    if not isinstance(trained_at, UndefinedType):
        params["trainedAt"] = trained_at
    
    if not isinstance(is_pinned, UndefinedType):
        params["isPinned"] = is_pinned
    
    if not isinstance(meta, UndefinedType):
        params["meta"] = meta
    
    return params
