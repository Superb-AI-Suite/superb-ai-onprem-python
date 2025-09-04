from typing import Optional, Dict, Any


def create_prediction_set_params(
    dataset_id: str,
    model_id: str,
    name: str,
    type: str,
    description: Optional[str] = None,
    annotations_count: Optional[int] = None,
    data_count: Optional[int] = None,
) -> Dict[str, Any]:
    """Convert parameters for create_prediction_set GraphQL mutation.
    
    Args:
        dataset_id (str): The dataset ID
        model_id (str): The model ID
        name (str): Name of the prediction set
        type (str): Type of the prediction set
        description (Optional[str]): Description of the prediction set
        annotations_count (Optional[int]): Number of annotations
        data_count (Optional[int]): Number of data items
        
    Returns:
        Dict[str, Any]: Parameters formatted for GraphQL mutation
    """
    params = {
        "datasetId": dataset_id,
        "modelId": model_id,
        "name": name,
        "type": type,
    }
    
    if description is not None:
        params["description"] = description
        
    if annotations_count is not None or data_count is not None:
        params["dataInfo"] = {}
        if annotations_count is not None:
            params["dataInfo"]["annotationsCount"] = annotations_count
        if data_count is not None:
            params["dataInfo"]["dataCount"] = data_count
    
    return params