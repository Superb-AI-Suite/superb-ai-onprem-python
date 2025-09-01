def delete_dataset_params(dataset_id: str):
    """Generate variables for delete dataset GraphQL mutation.
    
    Args:
        dataset_id (str): The ID of the dataset to delete.
        
    Returns:
        dict: Variables dictionary for the GraphQL mutation.
    """
    return {
        "dataset_id": dataset_id
    }