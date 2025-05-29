from typing import Optional
from spb_onprem.exceptions import BadParameterError


def dataset_params(
    dataset_id: Optional[str] = None,
    name: Optional[str] = None,
):
    """Get parameters for dataset lookup.
    
    Args:
        dataset_id: Optional dataset ID
        name: Optional dataset name
        
    Returns:
        dict: Parameters for dataset lookup
        
    Raises:
        ValueError: If neither id nor name is provided
    """
    if dataset_id is not None:
        return {"datasetId": dataset_id}
    elif name is not None:
        return {"name": name}
    else:
        raise BadParameterError("You must provide either id or name.")
