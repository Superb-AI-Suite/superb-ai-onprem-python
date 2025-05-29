

def delete_scene_params(
    dataset_id: str,
    data_id: str,
    scene_id: str,
):
    """Delete scene from selected data.

    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be deleted
        scene_id (str): scene id to be deleted
        
    Returns:
        dict: the params for graphql query
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "scene_id": scene_id,
    }
