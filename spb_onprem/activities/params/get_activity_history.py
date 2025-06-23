from typing import Dict, Any


def get_activity_history_params(
    dataset_id: str,
    activity_history_id: str,
) -> Dict[str, Any]:
    """Get parameters for getting activity history.
    
    Args:
        dataset_id (str): The ID of the dataset
        activity_history_id (str): The ID of the job
        
    Returns:
        Dict[str, Any]: The parameters for the query
    """
    return {
        "dataset_id": dataset_id,
        "job_history_id": activity_history_id,
    }
