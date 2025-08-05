from typing import Optional


def change_data_labeler_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
    labeler: Optional[str],
):
    """Make the variables for the changeDataLabeler query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        slice_id (str): The slice ID.
        labeler (Optional[str]): The labeler ID. None to unassign.
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "slice_id": slice_id,
        "labeler": labeler,
    } 