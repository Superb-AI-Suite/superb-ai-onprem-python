from typing import List, Union, Any
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.models.entities.model_train_class import ModelTrainClass


def update_model_params(
    dataset_id: str,
    model_id: str,
    name: Union[str, UndefinedType] = Undefined,
    description: Union[str, UndefinedType] = Undefined,
    training_classes: Union[List[ModelTrainClass], UndefinedType] = Undefined,
    model_content_id: Union[str, UndefinedType] = Undefined,
    is_trained: Union[bool, UndefinedType] = Undefined,
    trained_at: Union[str, UndefinedType] = Undefined,
    meta: Union[Any, UndefinedType] = Undefined,
):
    """Get parameters for updating a model.
    
    Args:
        dataset_id: The dataset ID
        model_id: The model ID
        name: Optional new name
        description: Optional new description
        training_classes: Optional new training classes
        model_content_id: Optional new model content ID
        is_trained: Optional new trained status
        trained_at: Optional new trained timestamp
        meta: Optional new metadata
        
    Returns:
        dict: Parameters for updating a model
    """
    params = {
        "datasetId": dataset_id,
        "id": model_id,
    }
    
    if not isinstance(name, UndefinedType):
        params["name"] = name
    
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
    
    if not isinstance(meta, UndefinedType):
        params["meta"] = meta
    
    return params
