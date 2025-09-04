from typing import Dict, Any


def update_prediction_set_data_info_params(
    dataset_id: str,
    id: str,
    annotation_count: int,
    data_count: int
) -> Dict[str, Any]:
    """Convert parameters for update_prediction_set_data_info GraphQL mutation.
    
    Args:
        dataset_id (str): The dataset ID
        id (str): The prediction set ID to update
        annotation_count (int): Number of annotations
        data_count (int): Number of data items
        
    Returns:
        Dict[str, Any]: Parameters formatted for GraphQL mutation
    """
    return {
        "datasetId": dataset_id,
        "updatePredictionSetId": id,
        "dataInfo": {
            "annotationsCount": annotation_count,
            "dataCount": data_count,
        }
    }