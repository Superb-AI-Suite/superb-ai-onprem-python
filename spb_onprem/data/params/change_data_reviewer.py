from typing import Optional


def change_data_reviewer_params(
    dataset_id: str,
    data_id: str,
    slice_id: str,
    reviewer: Optional[str],
):
    """Make the variables for the changeDataReviewer query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        slice_id (str): The slice ID.
        reviewer (Optional[str]): The reviewer ID. None to unassign.
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "slice_id": slice_id,
        "reviewer": reviewer,
    } 