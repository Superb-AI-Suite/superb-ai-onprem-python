from typing import Optional

from spb_onprem.exceptions import BadParameterError


def update_data_caption_params(
    dataset_id: str,
    data_id: str,
    caption: Optional[str] = None,
):
    """Make the variables for the updateDataCaption mutation.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        caption (Optional[str]): The new caption. None (or an empty string)
            clears the caption. The text is sent as given (no trimming).

    Returns:
        dict: The variables. ``caption`` is always sent, as null when None.
    """
    if not dataset_id:
        raise BadParameterError("dataset_id is required.")
    if not data_id:
        raise BadParameterError("data_id is required.")
    if caption is not None and not isinstance(caption, str):
        raise BadParameterError("caption must be a string or None.")
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "caption": caption,
    }
