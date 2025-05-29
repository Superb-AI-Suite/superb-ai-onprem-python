

def delete_annotation_version_params(
    dataset_id: str,
    data_id: str,
    version_id: str,
):
    """Delete annotation version from selected data.

    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be deleted
        version_id (str): annotation version id to be deleted
    """
    
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "id": version_id,
    }
