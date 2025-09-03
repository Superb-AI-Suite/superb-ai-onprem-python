def delete_model_params(dataset_id: str, model_id: str):
    """Generate variables for delete model GraphQL mutation.
    
    Args:
        dataset_id (str): The ID of the dataset.
        model_id (str): The ID of the model to delete.
        
    Returns:
        dict: Variables dictionary for the GraphQL mutation.
    """
    return {
        "dataset_id": dataset_id,
        "id": model_id
    }