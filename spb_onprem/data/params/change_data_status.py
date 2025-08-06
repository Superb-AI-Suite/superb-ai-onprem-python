from spb_onprem.data.enums.data_status import DataStatus


def change_data_status_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
    status: DataStatus,
):
    """Make the variables for the changeDataStatus query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        slice_id (str): The slice ID.
        status (DataStatus): The new status of the data slice.
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "slice_id": slice_id,
        "status": status.value,
    } 