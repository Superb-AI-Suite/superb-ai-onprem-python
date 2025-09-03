def delete_content_params(content_id: str):
    """Generate variables for delete content GraphQL mutation.
    
    Args:
        content_id (str): The ID of the content to delete.
        
    Returns:
        dict: Variables dictionary for the GraphQL query.
    """
    return {"id": content_id}