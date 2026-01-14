from spb_onprem.exceptions import BadParameterError


def delete_training_report_item_params(
    dataset_id: str,
    model_id: str,
    training_report_id: str,
):
    if dataset_id is None:
        raise BadParameterError("dataset_id is required.")
    if model_id is None:
        raise BadParameterError("model_id is required.")
    if training_report_id is None:
        raise BadParameterError("training_report_id is required.")

    return {
        "dataset_id": dataset_id,
        "model_id": model_id,
        "training_report_id": training_report_id,
    }
