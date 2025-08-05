def delete_slice_annotation_version_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
    id: str,
):
    """Delete slice annotation version from selected data.

    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be deleted from
        slice_id (str): slice id of the data
        id (str): annotation version id to be deleted

    Returns:
        dict: the params for graphql query
    """

    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "slice_id": slice_id,
        "id": id,
    } 