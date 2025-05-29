from spb_onprem.data.entities import Prediction


def insert_prediction_params (
    dataset_id: str,
    data_id: str,
    prediction: Prediction,
):
    """Insert prediction to selected data.

    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be inserted
        prediction (Prediction): prediction to be inserted

    Returns:
        dict: the params for graphql query
    """
    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "prediction": prediction.model_dump(
            by_alias=True, exclude_unset=True
        ),
    }
